from tabulate import tabulate
from task_2 import host_range_ping


def host_range_ping_tab():
    res_dict = host_range_ping()
    # columns = ['Доступные узлы', 'Недоступные узлы'] и только дойдя до задания 3 я понял зачем в разборе был словарь =)
    print(tabulate([res_dict], headers='keys', tablefmt="grid", stralign="center"))


if __name__ == "__main__":
    host_range_ping_tab()


