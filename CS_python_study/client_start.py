import csv
import random
import subprocess
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


while True:
    action = input('Start 10 clients (s) / '
                 'close client (x) /'
                 'Quit (q)')

    if action == 'q':
        print('Aplication closed')
        break
    elif action == 's':
        p_list.append(subprocess.Popen(f'gnome-terminal -- python3 server.py', shell=True))

        for _ in range(10):

            p_list.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n', shell=True))
        print('10 clients are start')
    elif action == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()


