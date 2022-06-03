import logging
import log.client_log_config
import argparse
import sys
from PyQt5.QtWidgets import QApplication

from general.constants import *
from general.utilites import *
from general.errors import ServerError
from client.client_db import ClientDB
from client.cargo import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

logger = logging.getLogger('client')


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        logger.critical(
            f'trying to run client with wrong port number {server_port}. Ports nuber from 1024 to 65535 are avalible now.')
        exit(1)

    return server_address, server_port, client_name


if __name__ == '__main__':
    server_address, server_port, client_name = argument_parser()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    logger.info(
        f'Client running: server: {server_address} , port: {server_port}, username: {client_name}')
    database = ClientDB(client_name)
    try:
        cargo = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    cargo.setDaemon(True)
    cargo.start()

    # Создаём GUI
    main_window = ClientMainWindow(database, cargo)
    main_window.make_connection(cargo)
    main_window.setWindowTitle(f'Chat application alpha release - {client_name}')
    client_app.exec_()
    cargo.transport_shutdown()
    cargo.join()