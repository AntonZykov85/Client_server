STR_1 = 'attribute'
STR_2 = 'класс'
STR_3 = 'функция'
STR_4 = 'type'

STR_LIST = [STR_1, STR_2, STR_3, STR_4]

for word in STR_LIST:
    try:
        bytes_list = bytearray(word, 'ascii')
    except UnicodeError:
        print(f'Word {word} cannot write in bytes type')
