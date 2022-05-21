from ipaddress import ip_address
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import socket

def host_ping(hosts_list):
    param = '-n' if platform.system().lower()=='windows' else '-c' # скриптик для того чтоб под разную ось не переписывать ключ
    # command = ['ping', hosts_list, param, '1', hosts_list] попробовал скрипт в скрипт, но увы, причем если просто попинговать через ф-ю колл оно работает, но колл не хочет итерироваться
    results = {'Reachable': "", 'Unreachable': ""}
    for address in hosts_list:
        try:
            address = ip_address(address)
        except ValueError:
            pass
        proc = subprocess.Popen(f"ping {address} -w {500} {param} {1}", stdout=subprocess.PIPE) # shell - false установлено по умолчанию
        proc.wait()

        if proc.returncode == 0:
            results['Reachable'] += f'{str(address)}\n'
            result_address = f'{address} - Узел доступен'
        else:
            results['Unreachable'] += f'{str(address)}\n'
            result_address = f'{address} - Узел недоступен'
        print(result_address)
    return results



if __name__ == '__main__':
    ip_addresses = ['yandex.ru', 'google.com', 'gb.ru', '0.0.255.12', '192.168.0.100', '192.168.0.101']
    host_ping(ip_addresses)


# сделал еще такую реализацию вместо обхода ошибки:
#         address = socket.gethostbyname(address)
#         address = ip_address(address)
#
#         но тогда в результате выдает следующее:
#         5.255.255.80 - Узел доступен
#         2.2.2.2 - Узел недоступен
#         192.168.0.100 - Узел недоступен
#         192.168.0.101 - Узел недоступен
# т.е. оно переводит буквенное имя узла в айпи, решил оставить как было в рекомендованной реализации. прошу сильно не ругаться ^_^
