
word_list = ['сетевое программирование', 'сокет', 'декоратор']

with open('test_file.txt', 'w', encoding='utf-8') as test_file:
        for line in word_list:
            test_file.write(f'{line}\n')
        test_file.close()


with open('test_file.txt', encoding='utf-8') as test_file:
    for lines in test_file:
        print(lines, end="")