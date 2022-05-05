import sys
import json
import socket
import time
import argparse

from launchpadlib.credentials import ServerError

from general.constants import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, MESSAGE, MESSAGE_TEXT, SENDER, DEFAULT_PORT
from general.utilites import get_message, send_message
import logging
import log.client_log_config
from decorators import logger
import random

client_logger = logging.getLogger('client')

# @logger
def get_message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
        print(f'Get message from Client {message[SENDER]}:  {message[MESSAGE_TEXT]}')
        client_logger.info(f'Get message from user {message[SENDER]}  :  {message[MESSAGE_TEXT]}')
    else:
        client_logger.error(f'incorrect server message {message}')

@logger
def message_new(sock, account_name='Guest'):
    message = input('Please input message for send to the chat or \'quit\' for close application ')
    if message == 'quit':
        sock.close()
        client_logger.info(f'App closed by user command')
        print('THX for using our application CYA')
        sys.exit(0)
    new_message = {
        ACTION: MESSAGE,
        TIME: time.ctime(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
        }
    client_logger.debug(f'New message dictory formed: {new_message}')
    return new_message


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
    mode_list = ['listen','send']
    mode_choice = random.choice(mode_list)
    parser = argparse.ArgumentParser()
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('adress', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('-mode', default=mode_choice, nargs='?')
    namespace = parser.parse_args(sys.argv[1:]) # get everything after scriptname
    server_address = namespace.adress
    server_port = namespace.port
    cliend_mode = namespace.mode


    if server_port < 1024 or server_port > 65535:
        client_logger.critical(
            f'Trying to run client with wrong port number {server_port}. Ports nuber from 1024 to 65535 are avalible now.')
        sys.exit(1)

    if cliend_mode not in mode_list:
        client_logger.critical(f'{cliend_mode} must be in {mode_list}')
        sys.exit(1)

    return server_address, server_port, cliend_mode



def main():
    server_address, server_port, cliend_mode = argument_parser()

    client_logger.info(f'server start with {server_port}, {server_address}, {cliend_mode}')

    try:
        cargo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cargo.connect((server_address, server_port))
        send_message(cargo, create_pref())
        answer = process_ans(get_message(cargo))
        client_logger.info(f'Connected with server {answer}')
        print(f'Connected with server')
    except json.JSONDecodeError:
        client_logger.error(f'Cannot decode JSON string')
        sys.exit(1)
    else:
        if  cliend_mode  == 'send':
            print('Send message mode is activated')
        else:
            print('Send write mode is activated')

        while True:
            if cliend_mode == 'send':
                try:
                    send_message(cargo, message_new(cargo))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    client_logger.error(f'Connection to server  {server_address} : {server_port} failed')
                    sys.exit(1)

            if cliend_mode == 'listen':
                try:
                    get_message_from_server(get_message(cargo))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    client_logger.error(f'Connection to server  {server_address} : {server_port} failed')
                    sys.exit(1)


if __name__ == '__main__':
    main()
