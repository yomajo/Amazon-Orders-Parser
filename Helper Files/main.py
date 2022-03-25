import sqlalchemy.sql.default_comparator    #neccessary for executable packing
from parser_constants import EXPECTED_SALES_CHANNELS, AMAZON_KEYS, ETSY_KEYS
from parser_utils import clean_phone_number, get_country_code, split_sku
from file_utils import get_output_dir, is_windows_machine, dump_to_json
from weights import OrderData
from database import SQLAlchemyOrdersDB
from parse_orders import ParseOrders
from datetime import datetime
import logging
import time
import sys
import csv
import os


# GLOBAL VARIABLES
TESTING = False
SALES_CHANNEL = 'AmazonCOM'
SKIP_ETONAS_FLAG = False
EXPECTED_SYS_ARGS = 4
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'
VBA_KEYERROR_ALERT = 'ERROR_IN_SOURCE_HEADERS'
VBA_OK = 'EXPORTED_SUCCESSFULLY'

if is_windows_machine():
    # ORDERS_SOURCE_FILE = r'C:\Coding\Ebay\Working\Backups\Etsy\EtsySoldOrders2022-1 24.csv'
    # ORDERS_SOURCE_FILE = r'C:\Coding\Ebay\Working\Backups\Amazon exports\EU 2022.02.23.txt'
    ORDERS_SOURCE_FILE = r'C:\Coding\Ebay\Working\Backups\Amazon exports\COM 2022.03.10.txt'
else:
    ORDERS_SOURCE_FILE = r'/home/devyo/Coding/Git/Amazon Orders Parser/Amazon exports/Collected exports/run4.txt'

# Logging config:
log_path = os.path.join(get_output_dir(client_file=False), 'loading_orders.log')
logging.basicConfig(handlers=[logging.FileHandler(log_path, 'a', 'utf-8')], level=logging.INFO)


def get_cleaned_orders(source_file:str, sales_channel:str, proxy_keys:dict) -> list:
    '''returns cleaned orders (as cleaned in clean_orders func) from source_file arg path'''
    delimiter = ',' if sales_channel == 'Etsy' else '\t'
    raw_orders = get_raw_orders(source_file, delimiter)
    cleaned_orders = clean_orders(raw_orders, sales_channel, proxy_keys)
    return cleaned_orders

def get_raw_orders(source_file:str, delimiter:str) -> list:
    '''returns raw orders as list of dicts for each order in txt source_file'''
    with open(source_file, 'r', encoding='utf-8') as f:
        source_contents = csv.DictReader(f, delimiter=delimiter)
        raw_orders = [{header : value for header, value in row.items()} for row in source_contents]
    return raw_orders

def clean_orders(orders:list, sales_channel:str, proxy_keys:dict) -> list:
    '''performs universal data cleaning for amazon and etsy raw orders data'''
    for order in orders:
        try:
            # split sku for each order without replacing original keys. sku str value replaced by list of skus
            order[proxy_keys['sku']] = split_sku(order[proxy_keys['sku']], sales_channel)
            if sales_channel == 'Etsy':
                # transform etsy country (Lithuania) to country code (LT)
                country = order[proxy_keys['ship-country']]
                order[proxy_keys['ship-country']] = get_country_code(country)
            else:
                # fix phone numbers in amazon from '+1 210-728-4548 ext. 01071' to a more friendly version
                order['buyer-phone-number'] = clean_phone_number(order['buyer-phone-number'])
        except KeyError as e:
            logging.critical(f'Failed while cleaning loaded orders. Last order: {order} Err: {e}')
            print(VBA_KEYERROR_ALERT)
            sys.exit()
    return orders


def parse_args(testing=False):
    '''returns arguments passed from VBA or hardcoded test environment'''
    if testing:
        print('--- RUNNING IN TESTING MODE. Using hardcoded args---')
        logging.warning('--- RUNNING IN TESTING MODE. Using hardcoded args---')
        assert SALES_CHANNEL in EXPECTED_SALES_CHANNELS, f'Unexpected sales_channel value passed from VBA side: {SALES_CHANNEL}'
        return ORDERS_SOURCE_FILE, SALES_CHANNEL, SKIP_ETONAS_FLAG

    try:
        assert len(sys.argv) == EXPECTED_SYS_ARGS, 'Unexpected number of sys.args passed'
        source_fpath = sys.argv[1]
        sales_channel = sys.argv[2]
        skip_etonas = True if sys.argv[3] == 'True' else False
        logging.info(f'Accepted sys args on launch: source_fpath: {source_fpath}; sales_channel: {sales_channel}; skip_etonas: {skip_etonas}. Whole sys.argv: {list(sys.argv)}')
        assert sales_channel in EXPECTED_SALES_CHANNELS, f'Unexpected sales_channel value passed from VBA side: {sales_channel}'
        return source_fpath, sales_channel, skip_etonas
    except Exception as e:
        print(VBA_ERROR_ALERT)
        logging.critical(f'Error parsing arguments on script initialization in cmd. Arguments provided: {list(sys.argv)} Number Expected: {EXPECTED_SYS_ARGS}.')
        sys.exit()

def main():
    '''Main function executing parsing of provided txt/csv file and outputing csv, xlsx files'''
    start_time = time.perf_counter()
    logging.info(f'\n\n NEW RUN STARTING: {datetime.today().strftime("%Y.%m.%d %H:%M")}')    
    source_fpath, sales_channel, skip_etonas = parse_args(testing=TESTING)
    
    # Define order dict keys to use
    proxy_keys = ETSY_KEYS if sales_channel == 'Etsy' else AMAZON_KEYS

    # Get cleaned source orders
    cleaned_source_orders = get_cleaned_orders(source_fpath, sales_channel, proxy_keys)
    
    db_client = SQLAlchemyOrdersDB(cleaned_source_orders, source_fpath, sales_channel, proxy_keys, testing=TESTING)
    new_orders = db_client.get_new_orders_only()
    logging.info(f'Loaded file contains: {len(cleaned_source_orders)}. Further processing: {len(new_orders)} orders')

    # Add additional data to orders
    logging.info(f'Passing new orders to add category, brand, (/mapped) weight data')
    orders_data_client = OrderData(new_orders, sales_channel, proxy_keys)
    weighted_orders = orders_data_client.add_orders_data()
    
    if TESTING:
        logging.warning(f'TESTING MODE. Unmapped sku export disabled. orders exported to json')
        dump_to_json(weighted_orders, 'debugging_orders.json')
    else:
        orders_data_client.export_unmapped_skus()

    # Parse orders, export target files
    ParseOrders(weighted_orders, db_client, proxy_keys, sales_channel).export_orders(testing=TESTING, skip_etonas=skip_etonas)
    print(VBA_OK)
    runtime = time.perf_counter() - start_time
    logging.info(f'\nRUN ENDED in: {runtime:.2f} sec. Timestamp: {datetime.today().strftime("%Y.%m.%d %H:%M")}\n')


if __name__ == "__main__":
    main()