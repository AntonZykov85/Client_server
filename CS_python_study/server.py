import socket
import sys
import json
import logging
import time

import log.server_log_config
from general.constants import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE,  MESSAGE_TEXT, SENDER
from general.utilites import get_message, send_message
from decorators import logger
import argparse
import select

server_logger = logging.getLogger('server')


@logger
def process_client_message(client_message, client_messages_list, client):
    server_logger.debug(f'Clients message {client_message} debugging')
    if ACTION in client_message and client_message[ACTION] == PRESENCE and TIME in client_message \
            and USER in client_message and client_message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return

    elif ACTION in client_message and client_message[ACTION] == MESSAGE and TIME in client_message \
            and MESSAGE_TEXT in client_message:
        client_messages_list.append((client_message[ACCOUNT_NAME], client_message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-adress', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:]) # get everything after scriptname
    listen_address = namespace.adress
    listen_port = namespace.port
    if listen_port < 1024 or listen_port > 65535:
        server_logger.critical(
            f'Trying to run client with wrong port number {listen_port}. Ports nuber from 1024 to 65535 are avalible now.')
        sys.exit(1)
    return listen_address, listen_port

def main():
    listen_address, listen_port = argument_parser()

    server_logger.info(f'server run with {listen_address}, {listen_port}')
    cargo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cargo.bind((listen_address, listen_port))
    cargo.listen(MAX_CONNECTIONS)
    cargo.settimeout(0.1)
    clients_list = []
    messages_list = []

    while True:
        try:
            client, client_address = cargo.accept()
        except OSError:
            pass

        else:
            server_logger.info(f'connected with client {client_address}')
            clients_list.append(client)
        finally:
            wait = 10
            r = []
            w = []
            try:
                if clients_list:
                     r, w, e = select.select(clients_list, clients_list, [], wait)
            except OSError:
                pass

            if r:
                for clients_with_message in r:
                    try:
                        process_client_message(get_message(clients_with_message), messages_list, clients_with_message)
                    except:
                        server_logger.info(f'Client  {clients_with_message.getpeername()} turn off from server')
                        clients_list.remove(clients_with_message)
            if w and messages_list:
                message_from_client = {
                    ACTION: MESSAGE,
                    SENDER: messages_list[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: messages_list[0][1]
                }
                del  messages_list[0]
                for waitig_client in w:
                    try:
                        send_message(waitig_client, message_from_client)
                    except:
                        server_logger.info(f'Client {waitig_client.getpeername()} turn off from server')
                        clients_list.remove(waitig_client)
           # try:
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


if __name__ == '__main__':
    main()
