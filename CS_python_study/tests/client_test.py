import sys
import os
import unittest
import time


sys.path.append(os.path.join(os.getcwd(), '..'))
from Client_server.CS_python_study.general.constants import DEFAULT_PORT, DEFAULT_IP_ADDRESS, MAX_CONNECTIONS, MAX_PACKAGE_LENGTH, \
ENCODING, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR

from Client_server.CS_python_study.client import process_ans

class Test_client(unittest.TestCase):

    def test_presence(self):
        test = {
        ACTION: PRESENCE,
        TIME: time.ctime(),
        USER: {
            ACCOUNT_NAME: 'Guest' #так как в ДЗ№3 я не делал функцию, а явно указывал, то тут приходится делать такжк
                }
            }

        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}) # if time make in '' - test will fallue

    def test_answer_200(self):
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    def test_answer_400(self):
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_response_wasted(self):
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Request'})

if __name__ == '__main__':
    unittest.main()