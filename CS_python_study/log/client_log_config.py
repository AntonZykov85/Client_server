import logging
import os
import sys

sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

client_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

#обработчик вывода в поток
crit_handler = logging.StreamHandler(sys.stderr)
crit_handler.setLevel(logging.CRITICAL)
crit_handler.setFormatter(client_formatter)

#обработчик вывода в файл
clientlog_file = logging.FileHandler(PATH, encoding='utf-8')
clientlog_file.setFormatter(client_formatter)

#регистратор
client_logger = logging.getLogger('client')
client_logger.addHandler(crit_handler)
client_logger.addHandler(clientlog_file)
client_logger.setLevel('DEBUG')

if __name__ == '__main__':
    client_logger.critical('cernel panic!!1')
    client_logger.error('attention error')
    client_logger.debug('debbuging info')
    client_logger.info('information message')
