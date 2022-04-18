import string
import csv

from chardet import detect


def get_data():
    list = ['Тип системы:', 'Название ОС:', 'Код продукта:', 'Изготовитель системы:']
    hh = []
    main_data  = []

    for i in range(1, 4):
        with open(f'info_{i}.txt') as f:
                data = open(f'info_{i}.txt', 'rb').read()
                result = detect(data)
                encode = result['encoding']
                print(encode)
                decode_text = data.decode(encode)
                with open(f'info_{i}.txt', 'w', encoding='utf-8') as new_file:
                    new_file.write(decode_text)

                    for line in f:
                            for el in list:
                                if el in line:
                                    os_prod_item = line.partition(el)[2].strip()
                                    hh.append(os_prod_item)

    system_type_list = hh[3:12:4]
    OS_list = hh[0:11:4]
    product_code_list = hh[1:11:4]
    producer_list = hh[2:12:4]

    main_data .append(list)

    for i in range(len(producer_list)):
        row_data = []
        row_data.append(system_type_list[i])
        row_data.append(OS_list[i])
        row_data.append(product_code_list[i])
        row_data.append(producer_list[i])
        main_data.append(row_data)

    return main_data


def write_to_csv(writen_file):

    main_data = get_data()
    with open(writen_file, 'w', encoding='utf-16') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in main_data:
            writer.writerow(row)

write_to_csv('done.csv')









