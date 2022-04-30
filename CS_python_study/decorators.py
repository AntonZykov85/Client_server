import sys, os
import logging
import log.client_log_config
import log.server_log_config
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def logger(logging_function):
    def logging_writer(*args, **kwargs):
        return_log = logging_function(*args, **kwargs)
        LOGGER.debug(f'{logging_function} was running with {args}, {kwargs} parametres.'
                     f'Running from module {logging_function.__module__}'
                     f' Running from function  {traceback.format_stack()[0].strip().split()[-1]}'
                     f' Running from function {inspect.stack()[1][3]}')
        return return_log

    return logging_writer


# class logger:
#     def __init__(self, *args):
#         self.args = args
#
#     def __call__(self, logging_function):
#         def logging_writer(*args, **kwargs):
#             return_log = logging_function(*args, **kwargs)
#             LOGGER.debug(f'{logging_function} was running with {args}, {kwargs} parametres.'
#                          f'Running from module {logging_function.__module__}'
#                          f' Running from function  {traceback.format_stack()[0].strip().split()[-1]}'
#                          f' Running from function {inspect.stack()[1][3]}')
#             return return_log
#
#         return logging_writer
