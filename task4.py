STR_1 = 'разработка'
STR_2 = 'администрирование'
STR_3 = 'protocol'
STR_4 = 'standard'

STR_LIST = [STR_1, STR_2, STR_3, STR_4]
BYTES_LIST = []

for word in STR_LIST:
    bytes_list = word.encode('utf-8')
    BYTES_LIST.append(bytes_list)

print(BYTES_LIST)

for word in BYTES_LIST:
    elem_list = word.decode('utf-8')
    print(elem_list)

