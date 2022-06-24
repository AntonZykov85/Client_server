""" Дескриптор. Инициализиция логера
метод определения модуля, источника запуска."""
import logging
import sys

logger = logging.getLogger('server_module')

if sys.argv[0].find('chat_client') == -1:
    logger = logging.getLogger('server_module')
else:
    logger = logging.getLogger('chat_client')


class Port:
    """ Класс - дескриптор для номера порта.
        Позволяет использовать только порты с 1023 по 65536. При попытке
        установить неподходящий номер порта генерирует исключение."""

    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'trying to run chat_client with wrong port number '
                f'{value}. Ports nuber from 1024 to 65535 '
                f'are avalible now.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
