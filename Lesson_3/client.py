import sys
import json
import socket
import time
from general.constants import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS
from general.utilites import get_message, send_message

def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    try:
        server_address = sys.argv[2]
        server_port = int(sys.argv[3])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = 7777
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

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

    send_message(cargo, message_to_server)
    try:
        answer = process_ans(get_message(cargo))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
