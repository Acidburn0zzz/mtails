import os
import shutil
import abc
import sh
import logging
from collections import OrderedDict
import inspect

import yaml
import yaml.resolver
import apt
import stem.control

from tails_server import _
from tails_server import file_util
from tails_server import tor_util
from tails_server import util
from tails_server import argument_parser
from tails_server import service_option_template

from tails_server.exceptions import TorIsNotRunningError
from tails_server.exceptions import UnknownOptionError
from tails_server.exceptions import ServiceNotInstalledError
from tails_server.exceptions import ServiceAlreadyEnabledError

from tails_server.config import HS_DIR, TOR_USER, TAILS_SERVER_USER, ADDITIONAL_SOFTWARE_CONFIG, \
    STATE_DIR, OPTIONS_FILE_NAME


class LazyOptionDict(OrderedDict):
    """Expects classes as its values. Returns an instance of the respective class."""
    def __init__(self, service, *args, **kwargs):
        self.service = service
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        item = super(LazyOptionDict, self).__getitem__(key)
        if inspect.isclass(item):
            logging.debug("Instantiating %r", item)
            self.__setitem__(key, item(self.service))
        return super(LazyOptionDict, self).__getitem__(key)


class TailsService(metaclass=abc.ABCMeta):

    arg_parser = argument_parser.ServiceParser()

    @classmethod
    def set_up_logging(cls, args):
        format_ = '%(levelname)s %(message)s'
        if args.verbose:
            logging.basicConfig(format=format_, level=logging.DEBUG)
        else:
            logging.basicConfig(format=format_, level=logging.INFO)
        logging.debug("args: %r", args)

    @property
    @abc.abstractmethod
    def name(self):
        """The name of the service, as used in the CLI.
        This should be the same as the basename of the service's script."""
        return str()

    @property
    def name_in_gui(self):
        """The name of the service, as displayed in the GUI."""
        return self.name.capitalize()

    @property
    @abc.abstractmethod
    def description(self):
        """A short description of the service, which will be displayed in the GUI."""
        return str()

    @property
    @abc.abstractmethod
    def client_application(self):
        """The name of the application which can connect to this service."""
        return str()

    @property
    def client_application_in_gui(self):
        """The name of the application which can connect to this service, as displayed in the
        GUI."""
        return self.client_application.capitalize()

    @property
    @abc.abstractmethod
    def packages(self):
        """Packages needed by this service.
        These will be installed when the service is installed."""
        return list()

    @property
    def systemd_service(self):
        """The name of the service's systemd service"""
        return self.name

    @property
    @abc.abstractmethod
    def default_target_port(self):
        """The default value of the service's target port (i.e. the port opened by the service on
        localhost) if the user does not specify a custom target port"""
        return int()

    @property
    def target_port(self):
        """The port opened by the service on localhost which should be forwarded via Tor"""
        if "target-port" in self.options_dict:
            return self.options_dict["target-port"].value
        return self.default_target_port

    @property
    def default_virtual_port(self):
        """The default value of the service's virtual port (i.e. the port exposed via the onion
        service) if the user does not specify a custom virtual port"""
        return self.default_target_port

    @property
    def virtual_port(self):
        """The port exposed via the onion service, i.e. the port clients have to use to connect to
        the service"""
        if "virtual-port" in self.options_dict:
            return self.options_dict["virtual-port"].value
        return self.default_virtual_port

    @property
    def connection_info(self):
        """A summary of all information necessary to connect to the service"""
        if self.address:
            s = str()
            s += _("Application: %s") % self.client_application_in_gui
            s += _("Address: %s:%s\n") % (self.address, self.virtual_port)
            s += _("Client Cookie: %s\n") % self.client_cookie
        return None

    @property
    def connection_info_in_gui(self):
        """The connection as it should be displayed in the GUI"""
        return self.connection_info

    @property
    @abc.abstractmethod
    def icon_name(self):
        """Name of the icon to use for this service in the GUI"""
        return str()

    documentation = str()
    persistent_paths = list()

    options = [
        service_option_template.AllowLanOption,
        service_option_template.PersistenceOption,
        service_option_template.AutoStartOption,
    ]

    _options_dict = None

    @property
    def options_dict(self):
        """A LazyOptionDict mapping the names of this service's options to the options' classes.
        The LazyOptionDict automatically instantiates an option the first time it is accessed,
        so then the dict maps the option's name to the option object.
        The reasoning for this is that instantiating an option usually requires disk reads and
        therefore is very slow, so we don't want to instantiate all the options when the GUI
        starts, because this would slow the start of the GUI down a lot. Instead we only
        instantiate the options when they are actually needed."""
        if not self._options_dict:
            self._options_dict = LazyOptionDict(
                self, [(option.name, option) for option in self.options])
        return self._options_dict

    _is_installed = "Not checked"

    @property
    def is_installed(self):
        logging.debug("is_installed: %r", self._is_installed)
        if self._is_installed == "Not checked":
            cache = apt.Cache()
            self._is_installed = all(cache[package].is_installed for package in self.packages)
        return self._is_installed

    @property
    def is_running(self):
        try:
            sh.systemctl("is-active", self.systemd_service)
        except sh.ErrorReturnCode_3:
            return False
        return True

    @property
    def is_persistent(self):
        if "persistence" not in self.options_dict:
            return False
        return self.options_dict["persistence"].value

    @property
    def is_published(self):
        if not self.address:
            return False
        return tor_util.is_published(self.address)

    @property
    def address(self):
        """
        The hidden service hostname aka onion address of this service.
        :return: onion address
        """
        try:
            with open(self.hs_hostname_file, 'r') as f:
                return f.read().split()[0].strip()
        except FileNotFoundError:
            return None

    @property
    def client_cookie(self):
        """The authentication cookie required to connect to this service.
        :return: client authentication cookie
        """
        try:
            with open(self.hs_hostname_file, 'r') as f:
                return f.read().split()[1].strip()
        except FileNotFoundError:
            return None

    @property
    def info_attributes(self):
        return OrderedDict([
            ("description", self.description),
            ("installed", self.is_installed),
            ("running", self.is_running),
            ("address", self.address),
            ("local-port", self.target_port),
            ("remote-port", self.virtual_port),
            ("persistent-paths", self.persistent_paths),
            ("options", OrderedDict([(option.name, option.value) for option in
                                     self.options_dict.values()])),
        ])

    @property
    def info_attributes_all(self):
        attributes = OrderedDict()
        attributes["name"] = self.name
        attributes["name-in-gui"] = self.name_in_gui
        attributes.update(self.info_attributes)
        attributes["hidden-service-dir"] = self.hs_dir
        attributes["packages"] = self.packages
        attributes["systemd-service"] = self.systemd_service
        attributes["icon-name"] = self.icon_name
        attributes["options"] = [option.info_attributes for option in self.options_dict.values()]
        return attributes

    @staticmethod
    def print_yaml(*args, **kwargs):
        def _dict_representer(dumper, data):
            return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                                            data.items())

        class OrderedDictDumper(yaml.Dumper):
            def ignore_aliases(self, data):
                return True

        OrderedDictDumper.add_representer(OrderedDict, _dict_representer)
        print(yaml.dump(*args, Dumper=OrderedDictDumper, default_flow_style=False, **kwargs))

    def __init__(self):
        self.state_dir = os.path.join(STATE_DIR, self.name)
        self.create_state_dir()
        self.hs_dir = os.path.join(HS_DIR, self.name)
        self.hs_hostname_file = os.path.join(self.hs_dir, "hostname")
        self.options_file = os.path.join(self.state_dir, OPTIONS_FILE_NAME)
        self._target_port = self.default_target_port
        self._virtual_port = self.default_virtual_port

    def get_status(self):
        return {"installed": self.is_installed,
                "enabled": self.is_running,
                "published": self.is_published}

    def print_status(self):
        status = self.get_status()
        self.print_yaml(status)

    def print_info(self, detailed=False):
        logging.debug("Getting attributes")
        attributes = self.info_attributes_all if detailed else self.info_attributes
        logging.debug("Dumping attributes")
        self.print_yaml(attributes)

    def enable(self, skip_add_onion=False):
        if self.is_running and self.is_published:
            raise ServiceAlreadyEnabledError("Service %r is already enabled" % self.name)
        logging.info("Enabling service %r" % self.name)

        if not tor_util.tor_has_bootstrapped():
            raise TorIsNotRunningError()

        if not self.is_installed:
            self.install()
        if not self.is_running:
            self.start()
        self.create_hs_dir()
        if not skip_add_onion:
            self.create_hidden_service()

    def install(self):
        logging.info("Installing packages: %s" % " ".join(self.packages))

        def update_packages():
            logging.info("Updating packages")
            cache.update()

        cache = apt.Cache()
        if any([package not in cache for package in self.packages]):
            update_packages()

        with util.PolicyNoAutostartOnInstallation():
            sh.apt_get("install", "-y", "-o", 'Dpkg::Options::=--force-confold',
                       "--no-install-recommends", self.packages)

        self.configure()

    def configure(self):
        """Initial configuration after installing the service"""
        for option in self.options_dict.values():
            option.value = option.default

    def install_using_apt_module(self):
        # There seems to be no way to automatically keep old config on conflicts with the apt module
        cache = apt.Cache()
        for package in self.packages:
            cache[package].mark_install()
        with util.PolicyNoAutostartOnInstallation():
            cache.commit()
        logging.info("Service %r installed", self.name)

    def uninstall(self):
        if self.is_running:
            self.disable()
        if self.is_persistent:
            self.remove_persistence()
        self.uninstall_packages()
        self.remove_options_file()
        self.remove_state_dir()
        if os.path.exists(self.hs_dir):
            self.remove_hs_dir()
        logging.info("Service %r uninstalled", self.name)

    def remove_persistence(self):
        logging.info("Removing persistence of service %r", self.name)
        self.options_dict["persistence"].value = False

    def uninstall_packages(self):
        # XXX: This could delete packages which were not installed by this service
        # (i.e. packages that are required by this service but were already installed)
        logging.info("Uninstalling packages: %s" % " ".join(self.packages))
        cache = apt.Cache()
        for package in self.packages:
            cache[package].mark_delete(purge=True)
        cache.commit()

    def create_state_dir(self):
        if not os.path.exists(self.state_dir):
            logging.debug("Creating state directory %r", self.state_dir)
            os.mkdir(self.state_dir)
        shutil.chown(self.state_dir, user=TAILS_SERVER_USER, group=TAILS_SERVER_USER)
        os.chmod(self.state_dir, 0o770)

    def remove_state_dir(self):
        logging.debug("Removing state directory %r", self.state_dir)
        shutil.rmtree(self.state_dir)

    def create_options_file(self):
        logging.debug("Creating empty options file for %r", self.name)
        with open(self.options_file, "w+") as f:
            yaml.dump(dict(), f)

    def remove_options_file(self):
        logging.info("Removing options file %r", self.options_file)
        os.remove(self.options_file)

    def create_hs_dir(self):
        logging.info("Creating hidden service directory %r", self.hs_dir)
        try:
            os.mkdir(self.hs_dir)
            os.chmod(self.hs_dir, 0o700)
        except FileExistsError:
            # The UID of debian-tor might change between Tails releases (it did before)
            # This would cause existing persistent directories to have wrong UIDs,
            # so we reset them here
            for dirpath, _, filenames in os.walk(self.hs_dir):
                for filename in filenames:
                    shutil.chown(os.path.join(dirpath, filename), TOR_USER, TOR_USER)
        shutil.chown(self.hs_dir, TOR_USER, TOR_USER)

    def remove_hs_dir(self):
        logging.info("Removing HS directory %r", self.hs_dir)
        shutil.rmtree(self.hs_dir)

    def start(self):
        logging.info("Starting service %r", self.name)
        sh.systemctl("start", self.systemd_service)

    def disable(self):
        self.stop()
        self.remove_hidden_service()

    def stop(self):
        logging.info("Stopping service %r", self.name)
        sh.systemctl("stop", self.systemd_service)

    def get_option(self, option_name):
        try:
            option = self.options_dict[option_name]
        except KeyError:
            raise UnknownOptionError("Service %r has no option %r" % (self.name, option_name))
        self.print_yaml({option.name: option.value})

    def set_option(self, option_name, value):
        if not self.is_installed:
            raise ServiceNotInstalledError("Service %r is not installed" % self.name)

        try:
            option = self.options_dict[option_name]
        except KeyError:
            raise UnknownOptionError("Service %r has no option %r" % (self.name, option_name))

        option.value = value
        option.apply()
        logging.debug("Option %r set to %r", option_name, value)
        return

    def reset_option(self, option_name):
        try:
            option = self.options_dict[option_name]
        except KeyError:
            raise UnknownOptionError("Service %r has no option %r" % (self.name, option_name))
        option.value = option.default
        option.apply()
        logging.debug("Option %r reset to %r", option_name, option.value)
        return

    def create_hidden_service(self):
        logging.info("Creating hidden service for %r", self.name)
        if not self.is_running:
            logging.warning("Refusing to create hidden service of not-running service %r",
                            self.name)
            return

        controller = stem.control.Controller.from_socket_file()
        controller.authenticate()
        controller.create_hidden_service(path=self.hs_dir,
                                         port=self.virtual_port,
                                         target_port=self.target_port,
                                         auth_type="basic",
                                         client_names=["client"])

    def remove_hidden_service(self):
        controller = stem.control.Controller.from_socket_file()
        controller.authenticate()
        controller.remove_hidden_service(self.hs_dir, self.virtual_port)

    # Reloading the torrc results in all SETCONF variables being overwritten, so this is
    # incompatible with setting HidServAuth with SETCONF. Also using stem's create_hidden_service
    # is a lot prettier than modifying the torrc
    # def create_hidden_service_via_torrc(self):
    #     if not self.is_running:
    #         logging.warning("Refusing to create hidden service of not-running service %r",
    #                         self.name)
    #         return
    #
    #     s = str()
    #     s += "HiddenServiceDir %s\n" % self.hs_dir
    #     s += "HiddenServicePort %s 127.0.0.1:%s\n" % (self.virtual_port, self.target_port)
    #     s += "HiddenServiceAuthorizeClient basic client\n"
    #     # Required to make hostname readable to tails-server
    #     s += "HiddenServiceDirGroupReadable 1\n"
    #
    #     file_util.ansible_add_hs_to_torrc(self.name, s)
    #
    #     # We have to restart tor here instead of reloading. Reloading would result in a sandbox
    #     # crash, because tor tries to access a new directory
    #     tor_util.restart_tor()
    #
    # def remove_hidden_service_via_torrc(self):
    #     file_util.ansible_remove_hs_from_torrc(self.name)
    #     tor_util.reload_tor()


    # stem uses the Tor control socket with ADD_ONION, which doesn't support client
    # authentication with Tor < 0.2.9.1. So we have to wait until this is available in Tails to
    # use stem.
    #
    # def create_hidden_service_with_stem(self):
    #     """Creating hidden service and setting address and hs_private_key accordingly"""
    #     if not self.is_running:
    #         logging.warning("Refusing to create hidden service of not-running service %r",
    #                         self.name)
    #         return
    #
    #     logging.debug("Adding HS with create_ephemeral_hidden_service")
    #
    #     try:
    #         key_type = "RSA1024"
    #         with open(self.hs_private_key_file, 'r') as f:
    #             key_content = f.read()
    #     except FileNotFoundError:
    #         key_type = "NEW"
    #         key_content = "RSA1024"
    #
    #     # We make client authentication non-optional until we have stable entry guards in Tails
    #     # if "client-authentication" in self.options_dict:
    #     #     client_auth = self.options_dict["client-authentication"].value
    #     # else:
    #     #     client_auth = None
    #     client_auth = {"client": None}
    #
    #
    #     controller = stem.control.Controller.from_port(port=TOR_CONTROL_PORT)
    #     controller.authenticate()
    #     # We have to use create_ephemeral_hidden_service() here instead of create_hidden_service(),
    #     # because the latter needs to access the filesystem, which is prevented by the Tor sandbox
    #     # see https://github.com/micahflee/onionshare/issues/179
    #     response = controller.create_ephemeral_hidden_service(
    #         ports={self.virtual_port: self.target_port},
    #         key_type=key_type,
    #         key_content=key_content,
    #         discard_key=False,
    #         detached=True,
    #         await_publication=True,
    #         # XXX: This option will be available in stem 1.5.0
    #         basic_auth=client_auth
    #     )
    #
    #     if response.service_id:
    #         self.set_onion_address(response.service_id)
    #     if response.private_key:
    #         self.set_hs_private_key(response.private_key)
    #     # XXX: Set client authentication
    #     if response.client_auth:
    #         self.set_client_auth(response.client_auth)
    #
    # def set_onion_address(self, address):
    #     with open(self.hs_hostname_file, 'w+') as f:
    #         f.write(address + ".onion")
    #
    # def remove_onion_address(self):
    #     os.remove(self.hs_hostname_file)
    #     os.remove(self.hs_private_key_file)
    #
    # def set_hs_private_key(self, key):
    #     with open(self.hs_private_key_file, 'w+') as f:
    #         f.write(key)
    #
    # def set_client_auth(self, client_auth):
    #     with open(self.hs_client_auth_file, 'w+') as f:
    #         f.write(client_auth)
    #
    # def remove_hidden_service_with_stem(self):
    #     if not self.address:
    #         logging.warning("Can't remove onion address of service %r: Address is not set",
    #                         self.name)
    #         return
    #     logging.debug("Removing HS with remove_ephemeral_hidden_service")
    #     controller = stem.control.Controller.from_port(port=TOR_CONTROL_PORT)
    #     controller.authenticate()
    #     controller.remove_ephemeral_hidden_service(self.address.replace(".onion", ""))

    def add_to_additional_software(self):
        lines = self.packages
        for line in lines:
            file_util.append_line_if_not_present(ADDITIONAL_SOFTWARE_CONFIG, line)

    def remove_from_additional_software(self):
        lines = self.packages
        for line in lines:
            file_util.remove_line_if_present(ADDITIONAL_SOFTWARE_CONFIG, line)

    def dispatch_command(self, args):
        if args.command == "info":
            return self.print_info(detailed=args.details)
        elif args.command == "status":
            return self.print_status()
        elif args.command == "install":
            return self.install()
        elif args.command == "uninstall":
            return self.uninstall()
        elif args.command == "enable":
            return self.enable()
        elif args.command == "disable":
            return self.disable()
        elif args.command == "get-option":
            return self.get_option(args.OPTION)
        elif args.command == "set-option":
            return self.set_option(args.OPTION, args.VALUE)
        elif args.command == "reset-option":
            return self.reset_option(args.OPTION)
