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

client_logger = logging.getLogger('client')

class ClientSender(threading.Thread, metaclass=ClientVerifer):
        def __init__(self, account_name, socket):
            self.account_name = account_name
            self.socket = socket
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
            new_message = {
                ACTION: MESSAGE,
                SENDER: self.account_name,
                DESTINATION: addresse,
                TIME: time.ctime(),
                MESSAGE_TEXT: message
                }
            client_logger.debug(f'New message dictory formed: {new_message}')
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
                  '"exit" - close application')

        def user_interface(self):
            self.print_help()
            while True:
                cmd = input('input command ')
                if cmd == 'message':
                    self.message_new()
                elif cmd == 'help':
                    self.print_help()
                elif cmd == 'exit':
                    try:
                        send_message(self.socket, self.last_message())
                    except:
                        pass
                        print('Finish connection')
                        client_logger.info('Connection finished by users command')
                        time.sleep(1)
                    break
                else:
                    print('Unknown command, try again. Input help for advises')


class ClientReader(threading.Thread, metaclass=ClientVerifer):
    def __init__(self, account_name, socket):
        self.account_name = account_name
        self.socket = socket
        super().__init__()

    def get_message_from_server(self):
            while True:
                try:
                    message = get_message(self.socket)
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message and MESSAGE_TEXT in message\
                            and message[DESTINATION] == self.account_name:
                        print(f'Get message from Client {message[SENDER]}:  {message[MESSAGE_TEXT]}')
                        client_logger.info(f'Get message from user {message[SENDER]}  :  {message[MESSAGE_TEXT]}')
                    else:
                        client_logger.error(f'incorrect server message {message}')
                except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    client_logger.critical(f'Connection lost')
                    break

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
