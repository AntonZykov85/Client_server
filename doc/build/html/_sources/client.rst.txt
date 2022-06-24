Client module
=====================================

Клиентское приложение для обмена сообщениями. Поддерживает отправку сообщений пользователям которые находятся в сети, сообщения шифруются с помощью алгоритма RSA с длинной ключа 2048 bit.

Поддерживает аргументы коммандной строки:

python client.py {имя сервера} {порт} -n или --name {имя пользователя} -p или -password {пароль}

{имя сервера} - адрес сервера сообщений.
{порт} - порт по которому принимаются подключения
-n или --name - имя пользователя с которым произойдёт вход в систему.
-p или --password - пароль пользователя.
Все опции командной строки являются необязательными, но имя пользователя и пароль необходимо использовать в паре.

Примеры использования:

python client.py
Запуск приложения с параметрами по умолчанию.

python client.py ip_address some_port
Запуск приложения с указанием подключаться к серверу по адресу ip_address:port

python -n test1 -p 123
Запуск приложения с пользователем test1 и паролем 123

python client.py ip_address some_port -n test1 -p 123
Запуск приложения с пользователем test1 и паролем 123 и указанием подключаться к серверу по адресу ip_address:port

client.py
Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

client. arg_parser ()
Парсер аргументов командной строки, возвращает кортеж из 4 элементов:

адрес сервера
порт
имя пользователя
пароль
Выполняет проверку на корректность номера порта.

database.py
.. autoclass:: chat_client.client_db.ClientDatabase
   :members:

transport.py
.. autoclass:: chat_client.cargo.ClientTransport
    :members:

main_window.py
.. autoclass:: chat_client.main_window.ClientMainWindow
    :members:

start_dialog.py
.. autoclass:: chat_client.start_dialog.UserNameDialog
    :members:


add_contact.py
.. autoclass:: chat_client.add_contacts.AddContactDialog
    :members:


del_contact.py
.. autoclass:: chat_client.delete_contacts.DelContactDialog
    :members: