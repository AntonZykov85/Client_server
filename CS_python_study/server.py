import socket
import sys
import json
import logging
import log.server_log_config
from general.constants import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from general.utilites import get_message, send_message
from decorators import logger

server_logger = logging.getLogger('server')

@logger
def process_client_message(client_message):
    server_logger.debug(f'Clients message {client_message} debugging')
    if ACTION in client_message and client_message[ACTION] == PRESENCE and TIME in client_message \
            and USER in client_message and client_message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            server_logger.critical(f'Trying to run client with wrong port number {listen_port}. Ports nuber from 1024 to 65535 are avalible now.')
            raise ValueError
    except IndexError:
        server_logger.info(f'После -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        server_logger.info(f'Порт - число от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        server_logger.info(f'После -\'a\'- необходимо указать IP адрес')
        sys.exit(1)
    server_logger.info(f'server is running with port: {listen_port}, adress: {listen_address}')

    cargo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cargo.bind((listen_address, listen_port))
    cargo.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = cargo.accept()
        server_logger.info(f'connected with client {client_address}')

        try:
            message_from_client = get_message(client)
            server_logger.info(f'get clients message: {message_from_client}')
            response = process_client_message(message_from_client)
            server_logger.info(f'Post answer to client {response}')
            send_message(client, response)
            server_logger.debug(f'connection with client {client_address} is close')
            client.close()
        except (ValueError, json.JSONDecodeError):
            server_logger.error(f'Принято некорретное сообщение от клиента {client_address}. Connection close')
            client.close()


if __name__ == '__main__':
    main()
