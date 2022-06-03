import logging
import sys

logger = logging.getLogger('server')



if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


class Port:
    def __set__(self, instance, value):
        if not 1023 < value <65536:
            logger.critical(f'rying to run client with wrong port number {value}. Ports nuber from 1024 to 65535 are avalible now.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name