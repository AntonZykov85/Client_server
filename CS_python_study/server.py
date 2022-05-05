import socket
import sys
import json
import logging
import time

import log.server_log_config
from general.constants import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE,  MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from general.utilites import get_message, send_message
from decorators import logger
import argparse
import select

server_logger = logging.getLogger('server')


@logger
def process_client_message(client_message, client_messages_list, client, clients_list, names):
    server_logger.debug(f'Clients message {client_message} debugging')
    if ACTION in client_message and client_message[ACTION] == PRESENCE and \
            TIME in client_message and USER in client_message:
        if client_message[USER][ACCOUNT_NAME] not in names.keys():
            names[client_message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Username is busy'
            send_message(client, response)
            clients_list.remove(client)
            client.close()
        return

    elif ACTION in client_message and client_message[ACTION] == MESSAGE and \
            DESTINATION in client_message and TIME in client_message \
            and SENDER in client_message and MESSAGE_TEXT in client_message:
        client_messages_list.append(client_message)
        return

    elif ACTION in client_message and client_message[ACTION] == EXIT and ACCOUNT_NAME in client_message:
        clients_list.remove(names[client_message[ACCOUNT_NAME]])
        names[client_message[ACCOUNT_NAME]].close()
        del names[client_message[ACCOUNT_NAME]]
        return

    else:
        response = RESPONSE_400
        response[ERROR] = 'Incorrect request'
        send_message(client, response)
        return


@logger
def process_message(message, names, listen_socks):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        server_logger.info(f'message end to user {message[DESTINATION]} '
                    f'from user {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        server_logger.error(
            f'User {message[DESTINATION]} is not register on server, cannot send message ')




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
    cargo.settimeout(0.5)
    clients_list = []
    messages_list = []
    names = dict()

    while True:
        try:
            client, client_address = cargo.accept()
        except OSError:
            pass

        else:
            server_logger.info(f'connected with client {client_address}')
            clients_list.append(client)

        # finally:
        read = []
        write = []
        errors = []
        try:
            if clients_list:
                    read, write, errors = select.select(clients_list, clients_list, [], 0)
        except OSError:
            pass

        if read:
                for clients_with_message in read:
                    try:
                        process_client_message(get_message(clients_with_message), messages_list, clients_with_message, clients_list, names)
                    except:
                        server_logger.info(f'Client  {clients_with_message.getpeername()} turn off from server')
                        clients_list.remove(clients_with_message)
        for i in messages_list:
            try:
                process_message(i, names, write)
            except Exception:
                server_logger.info(f'Connection with client {i[DESTINATION]} lost')
                clients_list.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages_list.clear()

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
