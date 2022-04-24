import sys
import json
import socket
import time
from general.constants import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS
from general.utilites import get_message, send_message
import logging
import log.client_log_config

client_logger = logging.getLogger('client')

def process_ans(message):
    client_logger.debug(f'debbuging info from server {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():

    try:
        server_address = int(sys.argv[2])
        server_port = int(sys.argv[3])
        if server_port < 1024 or server_port > 65535:
            client_logger.critical(f'Trying to run client with wrong port number {server_port}. Ports nuber from 1024 to 65535 are avalible now.')
            raise ValueError


    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = 7777
    except ValueError:
            sys.exit(1)

    client_logger.info(f'client with server adress {server_address} & port number {server_port} is run')

    cargo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # на винде требует явно прописать адрес
    cargo.connect((server_address, server_port))

    message_to_server = {
        ACTION: PRESENCE,
        TIME: time.ctime(),
        USER: {
            ACCOUNT_NAME: input('Введите имя авторизированного пользователя для входа или Guest для входя в гостевой режим \n')
        }
    }
    client_logger.debug(f'message {message_to_server} debuging')


    send_message(cargo, message_to_server)
    try:
        answer = process_ans(get_message(cargo))
        client_logger.info(f'servers answer {answer}')
        print(answer)
    except (ValueError, json.JSONDecodeError):
        client_logger.error('Не удалось декодировать сообщение сервера')
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
