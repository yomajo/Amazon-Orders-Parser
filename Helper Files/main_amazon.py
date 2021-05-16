from .amzn_parser_utils import get_output_dir, is_windows_machine, clean_phone_number
from .amzn_parser_constants import EXPECTED_AMZN_CHANNELS
from .etonas_xlsx_exporter import EtonasExporter
from .parse_orders import ParseOrders
from .orders_db import OrdersDB
from datetime import datetime
import logging
import sys
import csv
import os


# GLOBAL VARIABLES
TESTING = False
AMAZON_CHANNEL = 'EU'
SKIP_ETONAS_FLAG = False
EXPECTED_SYS_ARGS = 4
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'
VBA_KEYERROR_ALERT = 'ERROR_IN_SOURCE_HEADERS'
VBA_OK = 'EXPORTED_SUCCESSFULLY'

if is_windows_machine():
    TEST_AMZN_EXPORT_TXT = r'C:\Coding\Ebay\Working\Backups\Amazon exports\Collected exports\export 2021.04.29 EU.txt'
else:
    TEST_AMZN_EXPORT_TXT = r'/home/devyo/Coding/Git/Amazon Orders Parser/Amazon exports/Collected exports/run4.txt'

# Logging config:
log_path = os.path.join(get_output_dir(client_file=False), 'loading_amazon_orders.log')
logging.basicConfig(handlers=[logging.FileHandler(log_path, 'a', 'utf-8')], level=logging.INFO)


def get_cleaned_orders(source_file:str) -> list:
    '''returns cleaned orders (as cleaned in clean_orders func) from source_file arg path'''
    raw_orders = get_raw_orders(source_file)
    cleaned_orders = clean_orders(raw_orders)
    return cleaned_orders

def get_raw_orders(source_file:str) -> list:
    '''returns raw orders as list of dicts for each order in txt source_file'''
    with open(source_file, 'r', encoding='utf-8') as f:
        source_contents = csv.DictReader(f, delimiter='\t')
        raw_orders = [{header : value for header, value in row.items()} for row in source_contents]
    return raw_orders

def clean_orders(orders:list) -> list:
    '''replaces plus sign in phone numbers with 00'''
    for order in orders:
        try:
            order['buyer-phone-number'] = clean_phone_number(order['buyer-phone-number'])
        except KeyError as e:
            logging.warning(f'New header in source file. Alert VBA on new header. Error: {e}')
            print(VBA_KEYERROR_ALERT)
    return orders

def parse_export_orders(testing:bool, amzn_channel:str, skip_etonas:bool, cleaned_source_orders:list, loaded_txt:str):
    '''interacts with classes (ParseOrders, OrdersDB) to filter new orders, export desired files and push new orders to db'''
    db_client = OrdersDB(cleaned_source_orders, loaded_txt)
    new_orders = db_client.get_new_orders_only()
    logging.info(f'Loaded txt contains: {len(cleaned_source_orders)}. Further processing: {len(new_orders)} orders')
    ParseOrders(new_orders, db_client, amzn_channel).export_orders(testing=testing, skip_etonas=skip_etonas)

def parse_args():
    '''returns arguments passed from VBA'''
    try:
        assert len(sys.argv) == EXPECTED_SYS_ARGS, 'Unexpected number of sys.args passed'
        txt_path = sys.argv[1]
        amzn_channel = sys.argv[2]
        skip_etonas = True if sys.argv[3] == 'True' else False
        logging.info(f'Accepted sys args on launch: txt_path: {txt_path}; amzn_channel: {amzn_channel}; skip_etonas: {skip_etonas}. Whole sys.argv: {list(sys.argv)}')
        assert amzn_channel in EXPECTED_AMZN_CHANNELS, f'Unexpected amzn_channel value passed from VBA side: {amzn_channel}'
        return txt_path, amzn_channel, skip_etonas
    except Exception as e:
        print(VBA_ERROR_ALERT)
        logging.critical(f'Error parsing arguments on script initialization in cmd. Arguments provided: {list(sys.argv)} Number Expected: {EXPECTED_SYS_ARGS}.')
        sys.exit()

def main(testing, amazon_export_txt_path):
    '''Main function executing parsing of provided txt file and outputing csv, xlsx files'''
    logging.info(f'\n NEW RUN STARTING: {datetime.today().strftime("%Y.%m.%d %H:%M")}')    
    if testing:
        print('RUNNING IN TESTING MODE')
        txt_path = amazon_export_txt_path
        amzn_channel = AMAZON_CHANNEL
        skip_etonas = SKIP_ETONAS_FLAG    
    else:
        txt_path, amzn_channel, skip_etonas = parse_args()

    if os.path.exists(txt_path):
        cleaned_source_orders = get_cleaned_orders(txt_path)
        parse_export_orders(testing, amzn_channel, skip_etonas, cleaned_source_orders, txt_path)
        print(VBA_OK)
    else:
        logging.critical(f'Provided file {txt_path} does not exist.')
        print(VBA_ERROR_ALERT)
        sys.exit()
    logging.info(f'\nRUN ENDED: {datetime.today().strftime("%Y.%m.%d %H:%M")}\n')


if __name__ == "__main__":
    main(testing=TESTING, amazon_export_txt_path=TEST_AMZN_EXPORT_TXT)