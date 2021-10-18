from parser_constants import ORIGIN_COUNTRY_CRITERIAS, CATEGORY_CRITERIAS, BATTERY_BRANDS, CARDS_KEYWORDS
from parser_constants import DP_KEYWORDS, DPOST_TRACKED_COUNTRIES, LP_AMAZON_EU_REGISTRUOTA_COUNTRIES, LP_UK_BRANDS
from datetime import datetime
import platform
import logging
import shutil
import json
import sys
import os

# GLOBAL VARIABLES
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'

def get_product_category_or_brand(item_description:str, return_brand:bool=False) -> str:
    '''returns item category or brand based on item title. Last item in CATEGORY_CRITERIAS. Item before that - brand.
    Switch return index based on provided bool'''
    return_index = -1
    if return_brand:
        return_index = -2
    for criteria_set in CATEGORY_CRITERIAS:
        if criteria_set[0] in item_description.lower() and criteria_set[1] in item_description.lower():
            return criteria_set[return_index]
    return 'OTHER'

def get_hs_code(item_brand:str, item_category:str) -> str:
    '''returns hs code for etonas export file based on item brand and category'''
    # based on brand
    if item_brand == 'BOMB COSM' or item_brand == 'GELLI BAFF':
        return '3307'
    elif item_brand == 'INJINJI':
        return '6115'
    # based on category
    if item_category == 'BATTERIES':
        return '8506'
    elif item_category == 'PLAYING CARDS' or item_category == 'TAROT CARDS':
        return '9504 40'
    elif item_category == 'FOOTBALL':
        return '95'
    # unable to indentify
    return ''

def get_origin_country(item_description : str):
    '''returns item origin country based on products'''
    for criteria_set in ORIGIN_COUNTRY_CRITERIAS:
        if criteria_set[0] in item_description.lower() and criteria_set[1] in item_description.lower():
            return criteria_set[-1]
    return 'CN'

def get_level_up_abspath(absdir_path:str) -> str:
    '''returns abs directory path one level above provided dir as arg'''
    return os.path.dirname(absdir_path)

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

def uk_order_contains_lp_keywords(order:dict) -> bool:
    '''returns True if order item contains country-specific keywords target for LP shippment service (uses list of brand words)'''
    for keyword in LP_UK_BRANDS:
        if keyword in order['product-name'].upper():
            return True
    return False

def get_dpost_product_header_val(ship_country:str) -> str:
    '''returns PRODUCT header value for Deutsche Post csv'''
    if ship_country in DPOST_TRACKED_COUNTRIES:
        return 'GPT'    
    return 'GMP'

def clean_phone_number(phone_number:str) -> str:
    '''cleans phone numbers. Conditional reformatting for US based numbers
    Example: from +1 213-442-1463 ext. 90019 returns 00 90019 1 213-442-1463'''
    try:
        if ' ext. ' in phone_number:
            base_number, extension = phone_number.split(' ext. ')
            # searching plus position in base number
            plus_pos = base_number.find('+') + 1
            cleaned_number = base_number[:plus_pos] + ' ' +  extension + ' ' + base_number[plus_pos:]
        else:
            cleaned_number = phone_number
        return replace_phone_zero(cleaned_number)
    except Exception as e:
        logging.warning(f'Could not parse phone number: {phone_number} inside clean_phone_number util func. Err: {e}. Returning original number')
        return replace_phone_zero(phone_number)

def replace_phone_zero(phone_number:str) -> str:
    '''returns phone number with 00 insted of +. Example: +1-213-442 returns 001-213-442'''
    return phone_number.replace('+', '00')

def get_lp_registered_priority_value(order:dict, amzn_channel:str) -> str:
    '''based on ship country and amazon sales channel returns 1 or 0 as string to fill in
    Lietuvos Pastas 'Registruota' / 'Pirmenybinė/nepirmenybinė' header value'''
    if amzn_channel == 'COM':
        return '1'
    elif amzn_channel == 'EU':
        if order['ship-country'] in LP_AMAZON_EU_REGISTRUOTA_COUNTRIES:
            return '1'
        else:
            return ''
    else:
        logging.critical(f'Unexpected amzn_channel got up to get_lp_registruota_value func: {amzn_channel}. Retuning empty str')
        return ''

def create_src_file_backup(target_file_abs_path:str, backup_fname_prefix:str) -> str:
    '''returns abspath of created file backup'''
    src_files_folder = get_src_files_folder()
    _, backup_ext = os.path.splitext(target_file_abs_path)
    backup_abspath = get_backup_f_abspath(src_files_folder, backup_fname_prefix, backup_ext)
    shutil.copy(src=target_file_abs_path, dst=backup_abspath)
    logging.info(f'Backup created at: {backup_abspath}')
    return backup_abspath

def get_src_files_folder():
    output_dir = get_output_dir(client_file=False)
    target_dir = os.path.join(output_dir, 'src files')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
        logging.debug(f'src files directory inside Helper files has been recreated: {target_dir}')
    return target_dir

def get_backup_f_abspath(src_files_folder:str, backup_fname_prefix:str, ext:str) -> str:
    '''returns abs path for backup file. fname format: backup_fname_prefix-YY-MM-DD-HH-MM.ext'''
    timestamp = datetime.now().strftime('%y-%m-%d %H-%M')
    backup_fname = f'{backup_fname_prefix} {timestamp}{ext}'
    return os.path.join(src_files_folder, backup_fname)

def read_json_to_obj(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        orders = json.load(f)
    return orders

def delete_file(file_abspath:str):
    '''deletes file located in file_abspath'''
    try:
        os.remove(file_abspath)
    except FileNotFoundError:
        logging.warning(f'Tried deleting file: {file_abspath}, but apparently human has taken care of it first. (File not found)')
    except Exception as e:
        logging.warning(f'Unexpected err: {e} while flushing db old records, deleting file: {file_abspath}')


if __name__ == "__main__":
    pass