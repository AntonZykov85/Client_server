general_settings
=====================================

Пакет общих утилит, использующихся в разных модулях проекта.

Скрипт decorators.py
.. automodule:: general.decorators
    :members:

Скрипт descriptor.py
.. autoclass:: general.descriptor.Port
    :members:

Скрипт descriptor.py
.. autoclass:: general.errors.ServerError
   :members:

Скрипт metaclasses.py
.. autoclass:: general.metaclasses.ServerMaker
   :members:

.. autoclass:: general.metaclasses.ClientMaker
   :members:

Скрипт utilites.py
general.utilites. get_message (client)

Функция приёма сообщений от удалённых компьютеров. Принимает сообщения JSON, декодирует полученное сообщение и проверяет что получен словарь.
general.utilites. send_message (sock, message)

Функция отправки словарей через сокет. Кодирует словарь в формат JSON и отправляет через сокет.
Скрипт constants.py
Содержит разные глобальные переменные проекта.