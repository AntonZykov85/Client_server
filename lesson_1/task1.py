STR_1 = 'разработка'
STR_2 = 'сокет'
STR_3 = 'декоратор'

UNICODE_1 = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
UNICODE_2 = '\u0441\u043e\u043a\u0435\u0442'
UNICODE_3 = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

STR_LIST = [STR_1, STR_2, STR_3]
UNICODE_LIST = [UNICODE_1, UNICODE_2, UNICODE_3]

print("\nданные для строк\n")

for word in STR_LIST:
    print(type(word))
    print(word)


print("\nданные для юникода\n")

for word in UNICODE_LIST:
    print(type(word))
    print(word)

print("\n___________________________\n")

for word in STR_LIST:
    print(f"'{word}' - буквенный формат - {type(word)}")
    print(f"{word.encode('unicode_escape').decode('utf-8')} - набор кодовых точек - {type(word)}")