import socket
import sys
import json
import logging
import time

import log.server_log_config
from general.constants import *
from general.utilites import get_message, send_message
from decorators import logger
import argparse
import select
from metaclasses import ServerVerifier
from descriptor import Port

server_logger = logging.getLogger('server')

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-adress', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:]) # get everything after scriptname
    listen_address = namespace.adress
    listen_port = namespace.port
    # if listen_port < 1024 or listen_port > 65535:
    #     server_logger.critical(
    #         f'Trying to run client with wrong port number {listen_port}. Ports nuber from 1024 to 65535 are avalible now.')
    #     sys.exit(1)
    return listen_address, listen_port


class Serv(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_adress, listen_port):
        self.listen_adress = listen_adress
        self.listen_port = listen_port
        self.clients_list = []
        self.messages_list = []
        self.names = dict()

    def init_socket(self):
        server_logger.info(f'server run with {self.listen_adress}, {self.listen_port}')
        cargo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cargo.bind((self.listen_adress, self.listen_port))
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
                self. clients_list.append(client)

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
                    except:
                        server_logger.info(f'Client  {clients_with_message.getpeername()} turn off from server')
                        self.clients_list.remove(clients_with_message)
            for i in self.messages_list:
                try:
                    self.process_message(i, write) #!!!!!
                except Exception:
                    server_logger.info(f'Connection with client {i[DESTINATION]} lost')
                    self.clients_list.remove(self.names[i[DESTINATION]])
                    del self.names[i[DESTINATION]]
            self.messages_list.clear()

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            server_logger.info(f'message end to user {message[DESTINATION]} '
                               f'from user {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(
                f'User {message[DESTINATION]} is not register on server, cannot send message ')

    def process_client_message(self, message, client):
        server_logger.debug(f'Clients message {message} debugging')
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Username is busy'
                send_message(client, response)
                self.clients_list.remove(client)
                client.close()
            return

        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.client_messages_list.append(message)
            return

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients_list.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return

        else:
            response = RESPONSE_400
            response[ERROR] = 'Incorrect request'
            send_message(client, response)
            return


def main():
    listen_address, listen_port = argument_parser()
    server = Serv(listen_port, listen_address)
    server.main_loop()






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
