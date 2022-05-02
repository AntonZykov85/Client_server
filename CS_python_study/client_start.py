import csv
import subprocess
import os
import sys
# from subprocess import Popen, CREATE_NEW_CONSOLE

sys.path.append('../')
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.getcwd(), '..'))

# PATH = os.path.join(PATH, 'client.log')
p_list = []
args = ['/home/anton/PycharmProjects/Client_server/Client_server/CS_python_study','python client.py']
while True:
    action = input('Start 10 clients (s) / '
                 'close client (x) /'
                 'Quit (q)')

    if action == 'q':
        break
    elif action == 's':
        p_list.append(subprocess.Popen((args), shell=True))

        for _ in range(10):
            p_list.append(subprocess.Popen(args))
            print('10 clients are start')
    elif action == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()


