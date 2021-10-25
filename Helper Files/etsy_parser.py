from main_amazon import clean_orders, get_cleaned_orders, get_raw_orders
import csv


ETSY_FILE = 'sampleetsy.csv'
AMAZON_FILE = 'sampleCOM.txt'

def run():
    sales_channel = 'Etsy'
    read_file = ETSY_FILE

    delimiter = ',' if sales_channel == 'Etsy' else '\t'
    
    orders = get_raw_orders(read_file, delimiter)
    for i, order in enumerate(orders):
        # for header, value in order.items():
            # print(header, value)

        target_header = 'Order Type'
        val = order[target_header]
        if 0 < i < 100:
            print(f'order {i}: {target_header}: {val}')
        
        if i > 100:
            break


if __name__ == '__main__':
    run()
