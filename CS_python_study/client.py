import sys
import json
import socket
import time
import argparse
import threading
import dis
from launchpadlib.credentials import ServerError
from general.constants import *
from general.utilites import *
import logging
import log.client_log_config
from decorators import logger
import random
from metaclasses import ClientVerifer
from client_db import ClientDB

client_logger = logging.getLogger('client')
socket_locker = threading.Lock()
database_locker = threading.Lock()


class ClientSender(threading.Thread, metaclass=ClientVerifer):
        def __init__(self, account_name, socket, database):
            self.account_name = account_name
            self.socket = socket
            self.database = database
            super().__init__()

        def last_message(self):
            return {
                ACTION: EXIT,
                TIME: time.time(),
                ACCOUNT_NAME: self.account_name
            }

        def message_new(self):
            addresse = input('Please input destination username ')
            message = input('Please input message for send to the chat or \'quit\' for close application ')

            if message == 'quit':
                self.socket.close()
                client_logger.info(f'App closed by user command')
                print('THX for using our application CYA')
                sys.exit(0)

            with database_locker:
                if not self.database.check_user(addresse):
                    client_logger.error(f'Попытка отправить сообщение незарегистрированому получателю: {addresse}')
                    return

            new_message = {
                ACTION: MESSAGE,
                SENDER: self.account_name,
                DESTINATION: addresse,
                TIME: time.ctime(),
                MESSAGE_TEXT: message
                }
            client_logger.debug(f'New message dictory formed: {new_message}')

            with database_locker:
                self.database.save_message(self.account_name, addresse, message)

            with socket_locker:
                try:
                    send_message(self.socket, new_message)
                    client_logger.info(f'message send to user {addresse} ')
                except:
                    client_logger.critical(f'Connection lost')
                    sys.exit(1)

        def print_help(self):
            print('Commands: \n'
                  '"message" - send message; \n'
                  '"help" - display command advises \n'
                  '"exit" - close application \n'
                  '"history" - messages history \n'
                  '"edit" - edit contact list\n'
                  '"contacts" - show contact list')




        def user_interface(self):
            self.print_help()
            while True:
                command = input('input command: ')
                if command == 'message':
                    self.message_new()

                elif command == 'help':
                    self.print_help()

                elif command == 'exit':
                    with socket_locker:
                        try:
                            send_message(self.socket, self.last_message())
                        except:
                            pass
                        print('Connection finish')
                        client_logger.info('Connection finish by user command.')
                    time.sleep(0.5)
                    break

                elif command == 'contacts':
                    with database_locker:
                        contacts_list = self.database.get_contacts()
                    for contact in contacts_list:
                        print(contact)

                elif command == 'edit':
                    self.edit_contacts()


                elif command == 'history':
                    self.print_history()

                else:
                    print('Unknown command, try again. help - show user manual.')




        def print_history(self):
            ask = input('Sho income messages - in, outcome - out, all - Enter: ')
            with database_locker:
                if ask == 'in':
                    history_list = self.database.get_history(to_who=self.account_name)
                    for message in history_list:
                        print(f'\nMessage from user: {message[0]} from {message[3]}:\n{message[2]}')
                elif ask == 'out':
                    history_list = self.database.get_history(from_who=self.account_name)
                    for message in history_list:
                        print(f'\nMessage to user: {message[1]} from {message[3]}:\n{message[2]}')
                else:
                    history_list = self.database.get_history()
                    for message in history_list:
                        print(
                            f'\nMessage from user: {message[0]}, to user {message[1]} from {message[3]}\n{message[2]}')



        def edit_contacts(self):
            ans = input('For delete all input del, for add input - add: ')
            if ans == 'del':
                edit = input('input delete user name: ')
                with database_locker:
                    if self.database.check_contact(edit):
                        self.database.del_contact(edit)
                    else:
                        client_logger.error('trying to delete unknown contact.')
            elif ans == 'add':

                edit = input('Enter created contact name: ')
                if self.database.check_user(edit):
                    with database_locker:
                        self.database.add_contact(edit)
                    with socket_locker:
                        try:
                            add_contact(self.socket, self.account_name, edit)
                        except ServerError:
                            client_logger.error('Connot send packet to server.')


class ClientReader(threading.Thread, metaclass=ClientVerifer):
    def __init__(self, account_name, socket, database):
        self.account_name = account_name
        self.socket = socket
        self.database = database
        super().__init__()

    # def get_message_from_server(self):
    #         while True:
    #             try:
    #                 message = get_message(self.socket)
    #                 if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message and MESSAGE_TEXT in message\
    #                         and message[DESTINATION] == self.account_name:
    #                     print(f'Get message from Client {message[SENDER]}:  {message[MESSAGE_TEXT]}')
    #                     client_logger.info(f'Get message from user {message[SENDER]}  :  {message[MESSAGE_TEXT]}')
    #                 else:
    #                     client_logger.error(f'incorrect server message {message}')
    #             except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
    #                 client_logger.critical(f'Connection lost')
    #                 break

    def run(self):
        while True:
            time.sleep(1)
            with socket_locker:
                try:
                    message = get_message(self.socket)
                except OSError as err:
                    if err.errno:
                        client_logger.critical(f'Connection lost.')
                        break
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    client_logger.critical(f'Connection lost.')
                    break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                            and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                        print(f'\nMessage frome user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        with database_locker:
                            try:
                                self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except:
                                client_logger.error('Database error')

                        client_logger.info(f'Message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        client_logger.error(f'Uncorrect message frome server: {message}')


@logger
def process_ans(message):
            client_logger.debug(f'debbuging info from server {message}')
            if RESPONSE in message:
                if message[RESPONSE] == 200:
                    return '200 : OK'
                elif message[RESPONSE] == 400:
                    raise ServerError(f'400 : {message[ERROR]}')
            raise ValueError

@logger
def create_pref(account_name):
            output_mess = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: account_name}}
            client_logger.debug((f'{PRESENCE} for {account_name}'))
            return output_mess



@logger
def argument_parser():
    # mode_list = ['listen','send']
    # mode_choice = random.choice(mode_list) #don't need in this realize
    parser = argparse.ArgumentParser()
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('adress', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:]) # get everything after scriptname
    server_address = namespace.adress
    server_port = namespace.port
    client_username = namespace.name


    if server_port < 1024 or server_port > 65535:
        client_logger.critical(
            f'Trying to run client with wrong port number {server_port}. Ports nuber from 1024 to 65535 are avalible now.')
        sys.exit(1)

    # if cliend_mode not in mode_list:
    #     client_logger.critical(f'{cliend_mode} must be in {mode_list}')
    #     sys.exit(1)

    return server_address, server_port, client_username

def contacts_list_request(sock, name):
    client_logger.debug(f'request contact list fo user {name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    client_logger.debug(f'Request formed {req}')
    send_message(sock, req)
    ans = get_message(sock)
    client_logger.debug(f'Get answer {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def add_contact(sock, username, contact):
    client_logger.debug(f'Creating contact {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Creating contact error')
    print('Contact creation successful')


def user_list_request(sock, username):
    client_logger.debug(f'Get request known users {username}')
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def remove_contact(sock, username, contact):
    client_logger.debug(f'delete contact {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('delete contact error')
    print('delete successful')


def database_load(sock, database, username):
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        client_logger.error('request known urs error.')
    else:
        database.add_users(users_list)

    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        client_logger.error('request known urs error.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)

def main():
    print('this is client interface')

    server_address, server_port, client_username = argument_parser()

    if not client_username:
        client_username = input('Input your name')
    else:
        print(f'Client running with {client_username}')

    client_logger.info(f'server start with {server_port}, {server_address}, {client_username}')

    try:
        cargo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cargo.connect((server_address, server_port))
        send_message(cargo, create_pref(client_username))
        answer = process_ans(get_message(cargo))
        client_logger.info(f'Connected with server {answer}')
        print(f'Connected with server')
    except json.JSONDecodeError:
        client_logger.error(f'Cannot decode JSON string')
        sys.exit(1)
    else:
        database = ClientDB(client_username)
        database_load(cargo, database, client_username)
        handler = ClientReader(client_username, cargo)
        handler.daemon = True
        handler.start()
        user_interface_var = ClientSender(client_username, cargo)
        user_interface_var.daemon = True
        user_interface_var.start()
        client_logger.info(f'Processes started')

        while True:
            time.sleep(1)
            if handler.is_alive() and user_interface_var.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
