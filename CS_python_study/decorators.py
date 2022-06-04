import sys, os
import logging
import log.client_log_config
import log.server_log_config
import traceback
import inspect

if sys.argv[0].find('chat_client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('chat_client')


def logger(func_to_log):
        def log_saver(*args, **kwargs):
            logger.debug(
                f'Была вызвана функция {func_to_log.__name__} c параметрами {args} , {kwargs}. Вызов из модуля {func_to_log.__module__}')
            ret = func_to_log(*args, **kwargs)
            return ret
        return log_saver


# class logger:
#     # def __init__(self, *args):
#     #     self.args = args
#
#     def __call__(self, logging_function):
#         def logging_writer(*args, **kwargs):
#             return_log = logging_function(*args, **kwargs)
#             LOGGER.debug(f'{logging_function.__name__} was running with {args}, {kwargs} parametres.'
#                          f'Running from module {logging_function.__module__}'
#                          f' Running from function  {traceback.format_stack()[0].strip().split()[-1]}'
#                          f' Running from function {inspect.stack()[1][3]}')
#             return return_log
#
#         return logging_writer
