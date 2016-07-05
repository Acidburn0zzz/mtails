import sh
import logging
from gi.repository import Gtk, GLib, Gdk

from tails_server import services
from tails_server.gui.service import ServiceDecorator
from tails_server.gui.service_list import ServiceList
from tails_server.gui.service_chooser import ServiceChooser

from tails_server.config import ICON_DIR
from tails_server.config import MAIN_UI_FILE

service_modules_dict = services.import_service_modules()


class TailsServerGUI(object):

    current_service = None

    def on_window1_destroy(self, obj, data=None):
        for service in self.services:
            service.stop_status_monitor()
        Gtk.main_quit()

    def on_close_clicked(self, button):
        Gtk.main_quit()

    def on_button_add_service_clicked(self, button):
        ServiceChooser(self).show()

    def on_button_remove_service_clicked(self, button):
        service = self.service_list.get_selected_service()
        confirmed = self.obtain_confirmation(
            "Remove service",
            "This will irrevocably delete all configurations and data of this service, "
            "including the onion address. Are you sure you want to proceed?",
            ok_label="Remove"
        )
        if not confirmed:
            return
        service.run_threaded(self.uninstall_service, service)

    def uninstall_service(self, service):
        service.run_threaded(GLib.idle_add, service.config_panel.on_service_removal)
        service.uninstall()
        GLib.idle_add(self.service_list.remove_service, service)
        self.reset_service(service)

    def reset_service(self, service):
        i = self.services.index(service)
        new_service = service_modules_dict[service.name].service_class()
        self.services[i] = ServiceDecorator(self, new_service)

    def on_listbox_service_status_row_activated(self, listbox, listboxrow):
        self.service_list.row_selected(listboxrow)

    def obtain_confirmation(self, title, text, ok_label, cancel_label="Cancel"):
        try:
            sh.zenity(
                "--question",
                "--default-cancel",
                "--ok-label", ok_label,
                "--cancel-label", cancel_label,
                "--title", title,
                "--text", text,
            )
        except sh.ErrorReturnCode_1:
            return False
        return True

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(MAIN_UI_FILE)
        self.builder.connect_signals(self)

        self.services = [ServiceDecorator(self, module.service_class())
                         for module in service_modules_dict.values()]

        self.service_list = ServiceList(self)
        self.install_persistent_services()
        for service in [service for service in self.services if service.is_installed]:
            self.service_list.add_service(service)
        if self.service_list:
            self.service_list.select_service(self.service_list[0])

        icon_theme = Gtk.IconTheme.get_default()
        icon_theme.prepend_search_path(ICON_DIR)

        self.window = self.builder.get_object("window1")
        self.service_viewport_container = self.builder.get_object("box2")
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.window.connect("delete-event", Gtk.main_quit)
        self.window.set_title("Tails Server")
        self.window.show_all()

    def install_persistent_services(self):
        persistent_services = [service for service in self.services
                               if service.options_dict["persistence"].value]
        for service in [service for service in persistent_services if not service.is_installed]:
            service.install()

    def show_config_panel_placeholder(self):
        config_panel_container = self.builder.get_object("scrolledwindow_service_config")
        for child in config_panel_container.get_children():
            config_panel_container.remove(child)
        config_panel_container.add(self.builder.get_object("viewport_service_config_placeholder"))