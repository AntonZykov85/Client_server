Server module
=================================================

Серверный модуль мессенджера. Обрабатывает словари - сообщения, хранит публичные ключи клиентов.

Использование

Модуль подерживает аргементы командной стороки:

-p - Порт на котором принимаются соединения
-a - Адрес с которого принимаются соединения.
--no_gui Запуск только основных функций, без графической оболочки.
В данном режиме поддерживается только 1 команда: exit - завершение работы.
Примеры использования:

python server.py -p 8080

Запуск сервера на порту 8080

python server.py -a localhost

Запуск сервера принимающего только соединения с localhost

python server.py --no-gui

Запуск без графической оболочки

server.py
Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

server. arg_parser ()
Парсер аргументов командной строки, возвращает кортеж из 4 элементов:

адрес с которого принимать соединения
порт
флаг запуска GUI
server. config_load ()
Функция загрузки параметров конфигурации из ini файла. В случае отсутствия файла задаются параметры по умолчанию.
core.py
.. autoclass:: server_module.core.MessageProcessor
    :members:

database.py
.. autoclass:: server_module.server_db.ServerStorage
    :members:

main_window.py
.. autoclass:: server_module.main_window.MainWindow
    :members:

add_user.py
.. autoclass:: server_module.add_user.RegisterUser
    :members:

remove_user.py
.. autoclass:: server_module.delete_user.DelUserDialog
    :members:

config_window.py
.. autoclass:: server_module.config_window.ConfigWindow
    :members:

stat_window.py
.. autoclass:: server_module.stat_window.StatWindow
    :members: