import csv
import random
import subprocess
import time
import os
import sys
# from subprocess import Popen, CREATE_NEW_CONSOLE

# sys.path.append('../')
# PATH = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(os.getcwd(), '..'))

# PATH = os.path.join(PATH, 'client.log')
p_list = []
# args_c = ['/home/anton/PycharmProjects/Client_server/Client_server/CS_python_study','python client.py']
# args_s = ['/home/anton/PycharmProjects/Client_server/Client_server/CS_python_study','python server.py']
def client_name(i):
    return f'{random.getrandbits(128)}/{i}' # generate random 128-bit string


while True:
    action = input('Start application (s) / '
                 'close client (x) /'
                 'Quit (q)')

    if action == 'q':
        print('Application closed')
        break
    elif action == 's':
        client_numbers = int(input('input quantity of clients'))
        p_list.append(subprocess.Popen(f'gnome-terminal -- python3 server.py', shell=True))

        time.sleep(0.5)
        for i in range(client_numbers):
            # account = client_name(i)
            p_list.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n Test{i}', shell=True))
            print(f'user Test{i} enter chat')
        print(f'{client_numbers} clients are start')

    elif action == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()


