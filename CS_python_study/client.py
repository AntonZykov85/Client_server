import sys
import json
import socket
import time
import argparse
import threading

from launchpadlib.credentials import ServerError

from general.constants import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, MESSAGE, MESSAGE_TEXT, SENDER, DEFAULT_PORT, EXIT, DESTINATION
from general.utilites import get_message, send_message
import logging
import log.client_log_config
from decorators import logger
import random

client_logger = logging.getLogger('client')

@logger
def last_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@logger
def get_message_from_server(socket, sender_username):
    while True:
        try:
            message = get_message(socket)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message and MESSAGE_TEXT in message\
                    and message[DESTINATION] == sender_username:
                print(f'Get message from Client {message[SENDER]}:  {message[MESSAGE_TEXT]}')
                client_logger.info(f'Get message from user {message[SENDER]}  :  {message[MESSAGE_TEXT]}')
            else:
                client_logger.error(f'incorrect server message {message}')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            client_logger.critical(f'Connection lost')
            break

@logger
def message_new(sock, account_name='Guest'):
    addresse = input('Please input destination username ')
    message = input('Please input message for send to the chat or \'quit\' for close application ')
    if message == 'quit':
        sock.close()
        client_logger.info(f'App closed by user command')
        print('THX for using our application CYA')
        sys.exit(0)
    new_message = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: addresse,
        TIME: time.ctime(),
        MESSAGE_TEXT: message
        }
    client_logger.debug(f'New message dictory formed: {new_message}')
    try:
        send_message(sock, new_message)
        client_logger.info(f'message send to user {addresse} ')
    except:
        client_logger.critical(f'Connection lost')
        sys.exit(1)

def print_help():
    print('Commands: \n'
          '"message" - send message; \n'
          '"help" - display command advises \n'
          '"exit" - close application')

def user_interface(socket, username):
    print_help()
    while True:
        cmd = input('input command ')
        if cmd == 'message':
            message_new(socket, username)
        elif cmd == 'help':
            print_help()
        elif cmd == 'exit':
            send_message(socket, last_message(username))
            print('Finish connection')
            client_logger.info('Connection finished by users command')
            time.sleep(1)
            break
        else:
            print('Unknown command, try again. Input help for advises')


def create_pref(account_name='Guest'):
    output_mess = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name}}
    client_logger.debug((f'{PRESENCE} for {account_name}'))
    return output_mess


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
        handler = threading.Thread(target=get_message_from_server, args=(cargo, client_username), daemon=True)
        handler.start()
        user_interface_var = threading.Thread(target=user_interface, args=(cargo, client_username), daemon=True)
        user_interface_var.start()
        client_logger.info(f'Processes started')

        while True:
            time.sleep(1)
            if handler.is_alive() and user_interface_var.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
