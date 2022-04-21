import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from Client_server.Lesson_3.general.constants import DEFAULT_PORT, DEFAULT_IP_ADDRESS, MAX_CONNECTIONS, MAX_PACKAGE_LENGTH, \
ENCODING, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR

from Client_server.Lesson_3.server import process_client_message

class Test_server(unittest.TestCase):

    error = {RESPONSE: 400, ERROR: 'Bad Request'}
    valid = {RESPONSE: 200}

    def test_no_action(self):
        self.assertEqual(process_client_message(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.error)

    def test_wrong_action(self):
        self.assertEqual(process_client_message(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.error)

    def test_no_time(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.error)

    def test_wrong_user(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: '1.1', USER: {ACCOUNT_NAME: 'Wrong'}}), self.error)

    def test_valid_check(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.valid)

if __name__ == '__main__':
    unittest.main()









