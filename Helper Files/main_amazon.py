from etonas_xlsx_exporter import EtonasExporter
from amzn_parser_utils import get_output_dir
from parse_orders import ParseOrders
from orders_db import OrdersDB
from datetime import datetime
import logging
import sys
import csv
import os


# GLOBAL VARIABLES
TESTING = False
EXPECTED_SYS_ARGS = 3
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'
VBA_OK = 'EXPORTED_SUCCESSFULLY'
TEST_AMZN_EXPORT_TXT = r'C:\Coding\Amazon Orders Parser\Amazon exports\run1.txt'
# r'C:\Coding\Amazon Orders Parser\Amazon exports\amzn2.txt' ; r'C:\Coding\Amazon Orders Parser\Amazon exports\Collected exports\21510106877018387.txt'

# Logging config:
log_path = os.path.join(get_output_dir(client_file=False), 'loading_amazon_orders.log')
logging.basicConfig(handlers=[logging.FileHandler(log_path, 'a', 'utf-8')], level=logging.DEBUG)


def get_list_of_order_dicts(source_file, filter_order_id):
    orders = []
    txt_headers, txt_orders_data = parse_txt_file(source_file)
    try:
        for idx, order_row_data in enumerate(txt_orders_data):
            single_order_list = order_row_data.strip().split('\t')
            order_data_dict = single_order_data_to_dict(txt_headers, single_order_list)
            if order_data_dict['order-id'] == filter_order_id:
                logging.info(f'Found filtering ID: {filter_order_id}, filtering out {len(order_data_dict)}/{len(txt_orders_data)} orders')
                orders.clear()
                continue
            orders.append(order_data_dict)
        return orders
    except Exception as e:
        print(VBA_ERROR_ALERT)
        logging.critical(f'Error reading and splitting data {e}. Provided file: {source_file}. Error encountered in {idx}/{len(txt_orders_data)} orders')
        sys.exit()

def single_order_data_to_dict(txt_headers, single_order_list):
    order_data_dict = {}
    try:
        for txt_header, data_value in zip(txt_headers, single_order_list):
            order_data_dict[txt_header] = data_value
            # Replace telephone number plus with 00 for txt_header: 'buyer-phone-number'
            if txt_header == 'buyer-phone-number':
                order_data_dict[txt_header] = data_value.replace('+', '00')
        return order_data_dict
    except Exception as e:
        print(VBA_ERROR_ALERT)
        logging.critical(f'Error creating dict for single data row {e}. Collected dict thus far: {order_data_dict}')
        sys.exit()

def parse_txt_file(data_file):
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            txt_headers = f.readline().strip().split('\t')
            txt_data = f.readlines()
        return txt_headers, txt_data
    except Exception as e:
        print(VBA_ERROR_ALERT)
        logging.critical(f'Error reading txt source {e}')
        sys.exit()

def parse_export_orders(testing:bool, cleaned_source_orders:list, loaded_txt:str):
    '''interacts with classes (ParseOrders, OrdersDB) to filter new orders, export desired files and push new orders to db'''
    db_client = OrdersDB(cleaned_source_orders, loaded_txt)
    new_orders = db_client.get_new_orders_only()
    logging.info(f'Loaded txt contains: {len(cleaned_source_orders)}. Further processing: {len(new_orders)} orders')
    ParseOrders(new_orders, db_client).export_orders(testing)

def parse_args():
    if len(sys.argv) == EXPECTED_SYS_ARGS:
        txt_path, filter_order_id = sys.argv[1], sys.argv[2]
        logging.info(f'Accepted sys args on launch: txt_path: {txt_path}, filter_order_id: {filter_order_id}')
        return txt_path, filter_order_id
    else:
        print(VBA_ERROR_ALERT)
        logging.critical(f'Error parsing arguments on script initialization in cmd. Arguments provided: {len(sys.argv)} Expected: {EXPECTED_SYS_ARGS}')
        sys.exit()

def main(testing, amazon_export_txt_path):
    '''Main function executing parsing of provided txt file and outputing csv, xlsx files'''
    logging.info(f'\n NEW RUN STARTING: {datetime.today().strftime("%Y.%m.%d %H:%M")}')
    if not testing:
        txt_path, filter_order_id = parse_args()
    else:
        print('RUNNING IN TESTING MODE')
        txt_path, filter_order_id = amazon_export_txt_path, ''  #, '305-1937192-5680315'
    if os.path.exists(txt_path):
        logging.info('file exists, continuing to processing...')
        cleaned_source_orders = get_list_of_order_dicts(txt_path, filter_order_id)
        parse_export_orders(testing, cleaned_source_orders, amazon_export_txt_path)
        print(VBA_OK)
    else:
        logging.critical(f'Provided file {txt_path} does not exist.')
        print(VBA_ERROR_ALERT)
        sys.exit()
    logging.info(f'\nRUN ENDED: {datetime.today().strftime("%Y.%m.%d %H:%M")}\n')


if __name__ == "__main__":
    main(testing=TESTING, amazon_export_txt_path=TEST_AMZN_EXPORT_TXT)