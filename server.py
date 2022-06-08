import socket
import os
import argparse
import select
import threading
import configparser
from general.constants import *
from general.utilites import *
from descriptor import Port
from metaclasses import ServerVerifier
from server_module.server_db import ServerStorage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_statistic_model, ConfigWindow
from server_module.core import MessageProcessor
from server_module.server_db import ServerStorage
from server_module.main_window import MainWindow

server_logger = logging.getLogger('server_module')

# new_connection = False
# conflag_lock = threading.Lock()


def argument_parser(default_port, default_address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    server_logger.debug('Arguments loads.')
    return listen_address, listen_port, gui_flag

def config_load():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server_module.ini'}")
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config

def main():
    config = config_load()

    listen_address, listen_port, gui_flag = argument_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()
    if gui_flag:
        while True:
            command = input('Input "Exit" for exit')
            if command == 'exit':
                server.running = False
                server.join()
                break

    else:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        server_app.exec_()
        server.running = False


if __name__ == '__main__':
    main()
