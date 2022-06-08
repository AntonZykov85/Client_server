import socket
import sys
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from general.constants import *
from general.utilites import *
from general.errors import ServerError
import hashlib
import hmac
import binascii

sys.path.append('../')

logger = logging.getLogger('chat_client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username, password, keys):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.transport = None
        self.keys = keys
        self.password = password
        self.connection_init(port, ip_address)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'Connection lost')
                raise ServerError('Connection lost!')
            logger.error('Connection timeout when updating user lists')
        except json.JSONDecodeError:
            logger.critical(f'Connection lost')
            raise ServerError('Connection lost')
        self.running = True

    def connection_init(self, port, ip):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)
        connected = False
        for i in range(5):
            logger.info(f'Connection attempt No №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            logger.critical('Failed to connect to server_module')
            raise ServerError('Failed to connect to server_module')

        logger.debug('Server connection established')

        passwd_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        logger.debug(f'Passwd hash ready: {passwd_hash_string}')
        public_key = self.keys.publickey().export_key().decode('ascii')

        with socket_lock:
            presense = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: public_key
                }
            }
            logger.debug(f"Presense message = {presense}")

        try:
            send_message(self.transport, presense)
            ans = get_message(self.transport)
            logger.debug(f'Server response = {ans}.')
            if RESPONSE in ans:
                if ans[RESPONSE] == 400:
                    raise ServerError(ans[ERROR])
                elif ans[RESPONSE] == 511:
                    ans_data = ans[DATA]
                    hash = hmac.new(passwd_hash_string, ans_data.encode('utf-8'), 'MD5')
                    digest = hash.digest()
                    my_ans = RESPONSE_511
                    my_ans[DATA] = binascii.b2a_base64(
                        digest).decode('ascii')
                    send_message(self.transport, my_ans)
                    self.process_server_ans(get_message(self.transport))
        except (OSError, json.JSONDecodeError) as err:
            logger.debug(f'Connection error.', exc_info=err)
            raise ServerError('Connection failed during authorization process.')

        logger.info('The connection to the server_module was successfully established.')

    # def create_presence(self):
    #     out = {
    #         ACTION: PRESENCE,
    #         TIME: time.time(),
    #         USER: {
    #             ACCOUNT_NAME: self.username
    #         }
    #     }
    #     logger.debug(f'Message {PRESENCE} for user {self.username} formed')
    #     return out

    def process_server_ans(self, message):
        logger.debug(f'Parsing a message from the server_module: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.user_list_update()
                self.contacts_list_update()
                self.message_205.emit()
            else:
                logger.debug(f'Unknown verification code received {message[RESPONSE]}')

        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message and message[DESTINATION] == self.username:
                logger.debug(f'Message recived from user {message[SENDER]}:{message[MESSAGE_TEXT]}')
                self.new_message.emit(message)

    def contacts_list_update(self):
        self.database.contacts_clear()
        logger.debug(f'Request a contact list for a user {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        logger.debug(f'Request formed {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        logger.debug(f'Get answer {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            logger.error('Failed to update contact list.')

    def user_list_update(self):
        logger.debug(f'Query a list of known users {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            logger.error('Query a list of known Users')


    def key_request(self, user):
        logger.debug(f'Request users public key {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            logger.error(f'Failed to get buddy key{user}.')

    def add_contact(self, contact):
        logger.debug(f'Create contact {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def remove_contact(self, contact):
        logger.debug(f'Delete contact {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    def transport_shutdown(self):
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        logger.debug('Transport shuts down')
        time.sleep(0.5)

    def send_message(self, to, message):
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Message dictionary generated: {message_dict}')

        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_ans(get_message(self.transport))
            logger.info(f'Sent message to user {to}')

    def run(self):
        logger.debug('The process is running - the receiver of messages from the server_module.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Connection lost')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.debug(f'Connection lost')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    logger.debug(f'Message received from the server_module: {message}')
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)