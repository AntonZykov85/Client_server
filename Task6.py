import chardet
from chardet import detect

word_list = ['сетевое программирование', 'сокет', 'декоратор']

#создание файла, заполнение строками.
with open('test_file.txt', 'w', encoding='cp1251') as test_file:
        for line in word_list:
            test_file.write(f'{line}\n')
        test_file.close()

#проверка кодироки по умолчанию и конвертация
def encode_file():
    data = open('test_file.txt', 'rb').read()
    result = detect(data)
    encode = result['encoding']
    print(encode)
    decode_text = data.decode(encode)
    with open('test_file.txt', 'w', encoding='utf-8') as new_file:
        new_file.write(decode_text)

encode_file()



#принудительноткрытие в ютф-8
var = open('test_file.txt', 'r', encoding='utf-8').read()
# result_1 = detect(var)
# encode_1 = result_1['encoding']


print(var)