import logging
import logging.handlers
import os
import sys

sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

server_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

#обработчик вывода в поток
crit_handler = logging.StreamHandler(sys.stderr)
crit_handler.setLevel(logging.CRITICAL)
crit_handler.setFormatter(server_formatter)

#обработчик вывода в файл
serverlog_file = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='midnight')
serverlog_file.setFormatter(server_formatter)

#регистратор
server_logger = logging.getLogger('server_module')
server_logger.addHandler(crit_handler)
server_logger.addHandler(serverlog_file)
server_logger.setLevel('DEBUG')

if __name__ == '__main__':
    server_logger.critical('cernel panic!!1')
    server_logger.error('attention error')
    server_logger.debug('debbuging info')
    server_logger.info('information message')