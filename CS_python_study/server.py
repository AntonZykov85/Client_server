import configparser
import os
import socket
import sys
import json
import logging
import threading
import time
import log.server_log_config
from general.constants import *
from general.utilites import get_message, send_message
from decorators import logger
import argparse
import select
from metaclasses import ServerVerifier
from descriptor import Port
from server_db import ServerStorage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, ConfigWindow, create_statistic_model
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from errors import IncorrectDataRecivedError

server_logger = logging.getLogger('server')
new_connection = False
conflag_lock = threading.Lock()

def argument_parser(default_port, default_address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', default=default_port, type=int, nargs='?')
    parser.add_argument('-adress', default=default_address, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])  # get everything after scriptname
    listen_address = namespace.adress
    listen_port = namespace.port
    return listen_address, listen_port


class Serv(threading.Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.database = database
        self.clients_list = []
        self.messages_list = []
        self.names = dict()
        super().__init__()

    def init_socket(self):
        server_logger.info(f'server run with {self.listen_address}, {self.listen_port}')
        cargo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cargo.bind((self.listen_address, self.listen_port))
        cargo.listen(MAX_CONNECTIONS)
        cargo.settimeout(0.5)
        self.sock = cargo
        self.sock.listen()

    def main_loop(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                server_logger.info(f'connected with client {client_address}')
                self.clients_list.append(client)

            # finally:
            read = []
            write = []
            errors = []

            try:
                if self.clients_list:
                    read, write, errors = select.select(self.clients_list, self.clients_list, [], 0)
            except OSError:
                pass

            if read:
                for clients_with_message in read:
                    try:
                        self.process_client_message(get_message(clients_with_message), clients_with_message)
                    except (OSError):
                        server_logger.info(f'Client  {clients_with_message.getpeername()} turn off from server')
                        for name in self.names:
                            if self.names[name] == clients_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients_list.remove(clients_with_message)


            for message in self.messages_list:
                try:
                    self.process_message(message, write)  # !!!!!
                except(ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    server_logger.info(f'Connection with client {message[DESTINATION]} lost')
                    self.clients_list.remove(self.names[message[DESTINATION]])
                    self.database.user_logout(message[DESTINATION])
                    del self.names[message[DESTINATION]]
            self.messages_list.clear()

    def process_message(self, message, listen_socks):
        # message[DESTINATION] - имя
        # names[message[DESTINATION]] - получатель

        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            server_logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(
                f'User {message[DESTINATION]} is not register on server, cannot send message ')

    def process_client_message(self, message, client):
        global new_connection
        server_logger.debug(f'Clients message {message} debugging')

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Username is busy'
                send_message(client, response)
                self.clients_list.remove(client)
                client.close()
            return


        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and \
                TIME in message and SENDER in message and MESSAGE_TEXT in message and \
                self.names[message[SENDER]] == client:
            self.messages_list.append(message)
            self.database.process_message(message[SENDER], [DESTINATION])
            return

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients_list.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return

        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            send_message(client, response)


        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and \
                USER in message and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)


        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and \
                USER in message and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.users_list()]
            send_message(client, response)

        else:
            response = RESPONSE_400
            response[ERROR] = 'Incorrect request'
            send_message(client, response)
            return

# def print_help():
#     print('Available commands')
#     print('users - list of registered users')
#     print('connected - list of connected users')
#     print('history - logging history')
#     print('exit - turn off server')
#     print('help - user manual')

def main():
    config = configparser.ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/{"server.ini"}')
    listen_address, listen_port = argument_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = Serv(listen_address, listen_port, database)
    server.daemon = True
    server.start()
    server_app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.statusBar().showMessage('Server is working')
    main_window.active_clients_table.setModel(
        gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_statistic_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        # stat_window.show()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом!')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(config_window, 'Ошибка!', 'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)
    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()
    # while True:
    #     command = input('Input command: ')
    #     if command == 'help':
    #         print_help()
    #     elif command == 'exit':
    #         break
    #     elif command == 'users':
    #         for user in sorted(database.users_list()):
    #             print(f'User {user[0]}, last entrance: {user[1]}')
    #     elif command == 'connected':
    #         for user in sorted(database.active_users_list()):
    #             print(f'User {user[0]}, login: {user[1]}:{user[2]}, connecting time: {user[3]}')
    #     elif command == 'history':
    #         name = input(
    #             'Enter username. For looking history press Enter: ')
    #         for user in sorted(database.login_history(name)):
    #             print(f'User: {user[0]} login time: {user[1]}. Enter from: {user[2]}:{user[3]}')
    #     else:
    #         print('Unknown command')


if __name__ == '__main__':
    main()



#     message_from_client = get_message(client)
#     server_logger.info(f'get clients message: {message_from_client}')
#     response = process_client_message(message_from_client)
#     server_logger.info(f'Post answer to client {response}')
#     send_message(client, response)
#     server_logger.debug(f'connection with client {client_address} is close')
#     client.close()
# except (ValueError, json.JSONDecodeError):
#     server_logger.error(f'Принято некорретное сообщение от клиента {client_address}. Connection close')
#     client.close()


