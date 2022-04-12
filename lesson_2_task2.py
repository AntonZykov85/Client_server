import json

def write_order_to_json(item, quantity, price, buyer, date):

    with open('orders.json', 'r', encoding='utf-8') as file:
        objs = json.load(file)

    with open('orders', 'w', encoding='utf-8', ) as file_new:
        orders_list = objs['orders']
        dict_to_json = {'item': item, 'quantity': quantity,
                      'price': price, 'buyer': buyer, 'date': date}
        orders_list.append(dict_to_json)
        json.dump(objs, file_new, indent=4, ensure_ascii=False)


write_order_to_json('МФУ', '88', '33250', 'Puzo', '22.12.2020')
# write_order_to_json('Планшет', '14', '15000', 'Ivan Puzo', '16.12.1997')
