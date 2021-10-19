from main_amazon import clean_orders, get_cleaned_orders, get_raw_orders
import csv


ETSY_FILE = 'sampleetsy.csv'


# def get_raw_orders(source_file:str, delimiter:str) -> list:
#     '''returns raw orders as list of dicts for each order in txt source_file'''
#     with open(source_file, 'r', encoding='utf-8') as f:
#         source_contents = csv.DictReader(f, delimiter=delimiter)
#         raw_orders = [{header : value for header, value in row.items()} for row in source_contents]
#     return raw_orders

def run():
    sales_channel = 'Etsy'
    delimiter = ',' if sales_channel == 'Etsy' else '\t'
    
    print('trying to read')
    orders = get_raw_orders(ETSY_FILE, delimiter)
    for i, order in enumerate(orders):
        number_items = order['Number of Items']
        sku = order['SKU']
                
        if 0 < i < 10:
            print(f'order {i} has # items: {number_items}; SKUs: {sku}')
    
if __name__ == '__main__':
    run()
