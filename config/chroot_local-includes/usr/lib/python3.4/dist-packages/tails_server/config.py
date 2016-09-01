import os
PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))

APP_NAME = "tails-server"

TAILS_SERVER_USER = "tails-server"
TAILS_SERVER_CLIENT_USER = "tails-server-client"
DATA_DIR = "/usr/share/tails-server/"
STATE_DIR = "/var/lib/tails-server/"
OPTIONS_FILE_NAME = "options"
SERVICES_DIR = os.path.join(DATA_DIR, "services")
CLIENT_LAUNCHERS_DIR = os.path.join(DATA_DIR, "client-launchers")

TORRC = "/etc/tor/torrc"
TOR_DIR = "/var/lib/tor"
HS_DIR = os.path.join(TOR_DIR, "hidden_services")
TOR_USER = "debian-tor"
TOR_SERVICE = "tor@default.service"
TOR_BOOTSTRAPPED_TARGET = "tails-tor-has-bootstrapped.target"
TOR_CONTROL_PORT = 9051

PERSISTENCE_CONFIG = "/live/persistence/TailsData_unlocked/persistence.conf"
PERSISTENCE_DIR_NAME = "tails-server"
PERSISTENCE_DIR = os.path.join("/live/persistence/TailsData_unlocked", PERSISTENCE_DIR_NAME)

ADDITIONAL_SOFTWARE_CONFIG = "/live/persistence/TailsData_unlocked/live-additional-software.conf"

ANSIBLE_PLAYBOOK_DIR = os.path.join(DATA_DIR, "ansible_playbooks")
ICON_DIR = os.path.join(DATA_DIR, "icons")
MAIN_UI_FILE = os.path.join(DATA_DIR, "gui", "tails_server.ui")
CONFIG_UI_FILE = os.path.join(DATA_DIR, "gui", "service_config.ui")
SERVICE_CHOOSER_UI_FILE = os.path.join(DATA_DIR, "gui", "service_chooser.ui")
LOADING_WINDOW_UI_FILE = os.path.join(DATA_DIR, "gui", "loading_window.ui")
STATUS_UI_FILE = os.path.join(DATA_DIR, "gui", "status.ui")
SERVICE_LIST_UI_FILE = os.path.join(DATA_DIR, "gui", "service_list.ui")
SERVICE_OPTION_UI_FILE = os.path.join(DATA_DIR, "gui", "service_option.ui")
CONNECTION_INFO_UI_FILE = os.path.join(DATA_DIR, "gui", "connection_info.ui")
QUESTION_DIALOG_UI_FILE = os.path.join(DATA_DIR, "gui", "question_dialog.ui")
CLIENT_UI_FILE = os.path.join(DATA_DIR, "gui", "client_app.ui")