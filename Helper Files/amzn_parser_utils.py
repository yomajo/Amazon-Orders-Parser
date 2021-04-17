from amzn_parser_constants import ORIGIN_COUNTRY_CRITERIAS, CATEGORY_CRITERIAS, BATTERY_BRANDS, CARDS_KEYWORDS, DP_KEYWORDS, DPOST_TRACKED_COUNTRIES
import platform
import logging
import sys
import os

# GLOBAL VARIABLES
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'

def get_product_category(item_description : str):
    '''returns item category based on products'''
    for criteria_set in CATEGORY_CRITERIAS:
        if criteria_set[0] in item_description.lower() and criteria_set[1] in item_description.lower():
            return criteria_set[-1]
    return 'OTHER'

def get_origin_country(item_description : str):
    '''returns item origin country based on products'''
    for criteria_set in ORIGIN_COUNTRY_CRITERIAS:
        if criteria_set[0] in item_description.lower() and criteria_set[1] in item_description.lower():
            return criteria_set[-1]
    return 'CN'

def get_level_up_abspath(absdir_path):
        from os import path
        return path.dirname(absdir_path)

def get_total_price(order_dict : dict):
    '''returns a sum of 'item-price' and 'shipping-price' for given order'''
    try:
        item_price = order_dict['item-price']
        shipping_price = order_dict['shipping-price']
        return str(float(item_price) + float(shipping_price))
    except KeyError as e:
        logging.critical(f'Could not find item-price or shipping-price keys in provided dict: {order_dict} Error: {e}')
        print(VBA_ERROR_ALERT)
        sys.exit()
    except ValueError as e:
        logging.critical(f"Could not convert item-price or shipping-price to float. Both values: {order_dict['item-price']}; {order_dict['shipping-price']} Error: {e}")
        print(VBA_ERROR_ALERT)
        sys.exit()

def get_output_dir(client_file=True):
    '''returns target dir for output files depending on execution type (.exe/.py) and file type (client/systemic)'''
    # pyinstaller sets 'frozen' attr to sys module when compiling
    if getattr(sys, 'frozen', False):
        curr_folder = os.path.dirname(sys.executable)
    else:
        curr_folder = os.path.dirname(os.path.abspath(__file__))
    return get_level_up_abspath(curr_folder) if client_file else curr_folder

def file_to_binary(abs_fpath:str):
    '''returns binary data for file'''
    try:
        with open(abs_fpath, 'rb') as f:
            bfile = f.read()
        return bfile
    except FileNotFoundError as e:
        print(f'file_to_binary func got arg: {abs_fpath}; resulting in error: {e}')
        return None

def recreate_txt_file(abs_fpath:str, binary_data):
    '''outputs a file from given binary data'''
    try:
        with open(abs_fpath, 'wb') as f:
            f.write(binary_data)
    except TypeError:
        print(f'Expected binary when writing contents to file {abs_fpath}')

def is_windows_machine() -> bool:
    '''returns True if machine executing the code is Windows based'''
    machine_os = platform.system()
    return True if machine_os == 'Windows' else False

def order_contains_batteries(order:dict) -> bool:
    '''returns True if order item is batteries (uses list of brand words)'''
    for brand in BATTERY_BRANDS:
        if brand in order['product-name'].upper():
            return True
    return False

def order_contains_cards_keywords(order:dict) -> bool:
    '''returns True if order item is batteries (uses list of brand words)'''
    for keyword in CARDS_KEYWORDS:
        if keyword in order['product-name'].upper():
            return True
    return False

def uk_order_contains_dp_keywords(order:dict) -> bool:
    '''returns True if order item contains country-specific keywords (uses list of brand words)'''
    for keyword in DP_KEYWORDS:
        if keyword in order['product-name'].upper():
            return True
    return False

def get_order_service_lvl(ship_country:str) -> str:
    '''returns SERVICE_LEVEL DPost csv header value based on order country (Tracked or Priority)'''
    if ship_country in DPOST_TRACKED_COUNTRIES:
        return 'TRACKED'
    return 'PRIORITY'

if __name__ == "__main__":
    pass