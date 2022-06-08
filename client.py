import logging
import os

import log.client_log_config
import argparse
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

from general.constants import *
from general.utilites import *
from general.errors import ServerError
from chat_client.client_db import ClientDB
from chat_client.cargo import ClientTransport
from chat_client.main_window import ClientMainWindow
from chat_client.start_dialog import UserNameDialog
from Cryptodome.PublicKey import RSA

logger = logging.getLogger('chat_client')


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_passwd = namespace.password

    if not 1023 < server_port < 65536:
        logger.critical(
            f'trying to run chat_client with wrong port number {server_port}. Ports nuber from 1024 to 65535 are avalible now.')
        exit(1)

    return server_address, server_port, client_name, client_passwd


if __name__ == '__main__':
    server_address, server_port, client_name, client_passwd = argument_parser()
    client_app = QApplication(sys.argv)
    start_dialog = UserNameDialog()

    if not client_name or not client_passwd:
        client_app.exec_()

        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
            logger.debug(f'Using USERNAME = {client_name}, PASSWD = {client_passwd}.')
        else:
            exit(0)

    logger.info(
        f'Client running: server_module: {server_address} , port: {server_port}, username: {client_name}')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    database = ClientDB(client_name)

    try:
        cargo = ClientTransport(server_port, server_address, database, client_name, client_passwd, keys)
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Server error', error.text)
        exit(1)
    cargo.setDaemon(True)
    cargo.start()

    del start_dialog

    main_window = ClientMainWindow(database, cargo, keys)
    main_window.make_connection(cargo)
    main_window.setWindowTitle(f'Chat application alpha release - {client_name}')
    client_app.exec_()
    cargo.transport_shutdown()
    cargo.join()