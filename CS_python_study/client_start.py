import subprocess
import os
# from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []
while True:
    action = input('Start 10 clients (s) / '
                 'close client (x) /'
                 'Quit (q)')

    if action == 'q':
        break
    elif action == 's':
        p_list.append(subprocess.Popen('python server.py'))

        for _ in range(10):
            p_list.append(subprocess.Popen('python client.py'))
            print('10 clients are start')

    elif action == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()


