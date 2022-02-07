from parser_constants import ORIGIN_COUNTRY_CRITERIAS, CATEGORY_CRITERIAS, TRACKED_LP_SHIPMENT_TYPE, UNTRACKED_LP_SHIPMENT_TYPE
from countries import COUNTRY_CODES, GIFT_COUNTRIES
from string import ascii_letters
import logging
import random
import sys
import re


# GLOBAL VARIABLES
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'
VBA_KEYERROR_ALERT = 'ERROR_IN_SOURCE_HEADERS'
VBA_DPOST_CHARLIMIT_ALERT = 'DPOST_CHARLIMIT_WARNING'
DPOST_NAME_CHARLIMIT = 30


def get_sales_channel_category_brand(order:dict, product_name_proxy_key:str, return_brand:bool=False):
    '''returns hardcoded PLAYING CARDS for etsy orders and category/brand for Amazon order'''
    if product_name_proxy_key == '':
        return 'PLAYING CARDS'
    else:
        return get_product_category_or_brand(order[product_name_proxy_key], return_brand)

def get_product_category_or_brand(title:str, return_brand:bool=False) -> str:
    '''returns item category or brand based on item title. Last item in CATEGORY_CRITERIAS. Item before that - brand.
    Switch return index based on provided bool'''
    return_index = -2 if return_brand else -1
    for criteria_set in CATEGORY_CRITERIAS:
        if criteria_set[0] in title.lower() and criteria_set[1] in title.lower():
            return criteria_set[return_index]
    return 'OTHER'

def get_category_by_brand(brand_to_match:str) -> str:
    '''returns category by passed brand'''
    if brand_to_match == 'OTHER':
        return 'OTHER'
    for _, _, brand, category in CATEGORY_CRITERIAS:
        if brand_to_match == brand:
            return category
    return 'OTHER'

def get_sales_channel_hs_code(order:dict, product_name_proxy_key:str):
    '''returns HS code based on sales channel. Hardcoded for Etsy in case of no present title proxy key'''
    if product_name_proxy_key == '':
        return '9504 40'
    else:
        item_brand = get_product_category_or_brand(order[product_name_proxy_key], return_brand=True)
        item_category = get_product_category_or_brand(order[product_name_proxy_key])
        return get_hs_code(item_brand, item_category)

def get_hs_code(item_brand:str, item_category:str) -> str:
    '''returns hs code based on item brand and category. Updated on 2021.11'''
    # based on brand
    if item_brand == 'BOMB COSM':
        return '330499'

    # based on category
    if item_category == 'BATTERIES':
        return '850610'
    elif item_category == 'PLAYING CARDS' or item_category == 'TAROT CARDS':
        return '950440'
    else:
        return '950300'

def get_origin_country(title:str):
    '''returns item origin country based on product title'''
    for criteria_set in ORIGIN_COUNTRY_CRITERIAS:
        if criteria_set[0] in title.lower() and criteria_set[1] in title.lower():
            return criteria_set[-1]
    return 'CN'

def get_total_price(order:dict, sales_channel:str, return_as_float:bool=False):
    '''returns a total order price based on sales channel. Default returns as str, optionally: as float'''
    try:
        if sales_channel == 'Etsy':
            # use formula: Order Value - Discount Amount + Shipping
            order_value = float(order['Order Value'])
            discount = float(order['Discount Amount'])
            shipping = float(order['Shipping'])
            total = round(order_value - discount + shipping, 2)
            return total if return_as_float else str(total)
        else:
            # For amazon orders, total = item-price + shipping-price
            item_price = float(order['item-price'])
            shipping_price = float(order['shipping-price'])
            total = round(item_price + shipping_price, 2)
            return total if return_as_float else str(total)
    except KeyError as e:
        logging.critical(f'Failed in get_total_price. Sales ch: {sales_channel}; order: {order} Key err: {e}')
        print(VBA_KEYERROR_ALERT)
        sys.exit()
    except ValueError as e:
        logging.critical(f'Failed in get_total_price. Sales ch: {sales_channel}; order: {order}. Err: {e}')
        print(VBA_ERROR_ALERT)
        sys.exit()

def get_dpost_product_header_val(order:dict) -> str:
    '''returns PRODUCT header value for Deutsche Post csv'''
    try:
        return 'GPT' if order['tracked'] else 'GMP' 
    except Exception as e:
        logging.critical(f'Failed while accessing order category key in get_dpost_product_header_val util func. Order: {order} Returning GMP. Err: {e}')
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

def get_lp_priority(order:dict) -> str:
    '''returns 1 or '' as string to fill in Lietuvos Pastas 'Pirmenybinis siuntimas' header value'''
    try:
        if order['tracked']:
            return '1'
        else:
            return '1' if order['vmdoption'] != '' and order['vmdoption'] != 'VKS' else ''
    except Exception as e:
        logging.critical(f'Failed in get_lp_registered_priority_value util func. Order: {order}. Err: {e}')
        return ''

def get_order_ship_price(order:dict, proxy_keys:dict) -> float:
    '''returns order shipping price as float'''
    try:
        target_key = proxy_keys['shipping-price']
        return float(order[target_key])
    except KeyError:
        logging.critical(f'Key error: Could not find column: \'{target_key}\' in data source. Exiting on order: {order}')
        print(VBA_KEYERROR_ALERT)
        sys.exit()
    except Exception as e:
        logging.warning(f'Error retrieving \'{target_key}\' in order: {order}, returning 0 (integer). Error: {e}')
        return 0

def get_order_country(order:dict, proxy_keys) -> str:
    '''returns order destination country code. Called from ParseOrders'''
    try:
        target_key = proxy_keys['ship-country']
        return order[target_key]
    except KeyError:
        logging.critical(f'Could not find column: \'shipping-country\' in data source. Exiting on order: {order}. Terminating immediately')
        print(VBA_KEYERROR_ALERT)
        sys.exit()
    except Exception as e:
        logging.critical(f'Error retrieving ship-country in order: {order}, returning empty string. Error: {e}')
        print(VBA_KEYERROR_ALERT)
        sys.exit()

def get_country_code(country:str) -> str:
    '''using COUNTRY_CODES dict, returns 2 letter str for country if len(country) > 2. Called from main'''
    try:
        if len(country) > 2:
            country_code = COUNTRY_CODES[country.upper()]
            return country_code
        else:
            return country
    except KeyError as e:
        logging.critical(f'Failed to get country code for: {country}. Err:{e}. Alerting VBA, terminating immediately')
        print(VBA_ERROR_ALERT)
        sys.exit()

def get_inner_qty_sku(original_code:str, quantity_pattern:str):
    '''returns recognized internal quantity from passed regex pattern: quantity_pattern inside original_code arg and simplified code
    two examples: from codes: '(3 vnt.) CR2016 5BL 3V VINNIC LITHIUM' / '1 vnt. 1034630' ->
    return values are: 3, 'CR2016 5BL 3V VINNIC LITHIUM' / 1, '1034630' '''
    try:
        quantity_str = re.findall(quantity_pattern, original_code)[0]
        inner_quantity = int(re.findall(r'\d+', quantity_str)[0])
        inner_code = original_code.replace(quantity_str, '')
        return inner_quantity, inner_code
    except:
        return 1, original_code

def shorten_word_sequence(long_seq : str) -> str:
    '''replaces middle names with abbreviations. Example input: Jose Inarritu Gonzallez Ima La Piena Hugo
    Output: Jose I. G. I. L. P. Hugo'''
    shortened_seq_lst = []
    long_seq = long_seq.replace('-',' ')    # Treatment of dashes inside name string
    try:
        words_inside = long_seq.split()
        for idx, word in enumerate(words_inside):
            if idx == 0 or idx == len(words_inside) - 1:
                shortened_seq_lst.append(word)
            else:
                abbr_word = abbreviate_word(word)
                shortened_seq_lst.append(abbr_word)
        short_seq = ' '.join(shortened_seq_lst)
        assert len(short_seq) <= DPOST_NAME_CHARLIMIT, 'Shortened name did not pass charlimit validation'
        return short_seq        
    except Exception as e:
        logging.warning(f'Could not shorten name: {long_seq}. Error: {e}. Alerting VBA, returning unedited')
        print(VBA_DPOST_CHARLIMIT_ALERT)
        return long_seq

def abbreviate_word(word : str) -> str:
    '''returns capitalized first letter with dot of provided word if it stars with letter'''            
    return word[0].upper() + '.' if word[0] in ascii_letters else word

def split_sku(split_sku:str, sales_channel:str) -> list:
    '''splits sku string on ',' and ' + ' into list of skus for Etsy.
    example input: '1 vnt. 1040830 + 1 vnt. 1034630,1 vnt. T1147'
    return value: ['1 vnt. 1040830', '1 vnt. 1034630', '1 vnt. T1147']
    
    for Amazon, only splits multilistings on plus ' + ' string'''
    if sales_channel == 'Etsy':
        plus_comma_split = [sku_sublist.split(',') for sku_sublist in split_sku.split(' + ')]
        return [sku for sku_sublist in plus_comma_split for sku in sku_sublist]
    else:
        return split_sku.split(' + ')

def alert_VBA_duplicate_mapping_sku(sku_code:str):
    '''duplicate SKU code found when reading mapping xlsx, alerts VBA, logs sku_code with warning level'''
    logging.warning(f'Duplicate SKU code found in mapping xlsx. User has been warned. SKU code found at least twice: {sku_code}')
    print(f'DUPLICATE SKU IN MAPPING: {sku_code}')

def get_LP_siuntos_rusis_header(vmdoption:str, tracked:bool):
    '''returns 'siuntos rusis' header value for LP csv'''
    try:
        shipment_type_dict = TRACKED_LP_SHIPMENT_TYPE if tracked else UNTRACKED_LP_SHIPMENT_TYPE
        return shipment_type_dict[vmdoption]
    except:
        return vmdoption

def engineer_total(country_code:str, order_total:float, order_id:str) -> float:
    '''based on order_total and country_code, returns financially engineered total for export files'''
    try:
        if country_code in ['BR', 'BY'] and order_total > 10:
            engineered_total = round(random.uniform(6, 9.98), 2)
            logging.warning(f'{order_id} (to: {country_code}) total-engineered key has new random value: {engineered_total}')            
            return engineered_total
        elif country_code in GIFT_COUNTRIES and order_total > 20:
            engineered_total = round(random.uniform(15, 19.98), 2)
            logging.warning(f'{order_id} (to: {country_code}) total-engineered key has new random value: {engineered_total}')
            return engineered_total
        else:
            return order_total
    except Exception as e:
        logging.error(f'engineer_total function error on order_id: {order_id}. Args: country: {country_code}, order_total: {order_total}. \
            Returning original order_total. Err: {e}')
        return order_total

def enter_LP_address(header:str, order:dict, proxy_keys:dict) -> str:
    '''returns address string for LP csv file'''
    # disposable address fields (etsy has no address3)
    address1 = order[proxy_keys['ship-address-1']]
    address2 = order[proxy_keys['ship-address-2']]
    add3_key = proxy_keys.get('ship-address-3','')
    address3 = order.get(add3_key, '')
    # country LT -> use "Gavëjo gatvė", "Adreso eilutė 1" fields for other countries use "Adreso eilutė 2", "Adreso eilutė 2"
    if get_order_country(order, proxy_keys) == 'LT':
        if header == 'Gavėjo gatvė':
            return address1
        elif header == 'Adreso eilutė 1':
            return address2
        else:
            # header == Adreso eilutė 2
            return address3
    else:
        if header == 'Adreso eilutė 1':
            return address1
        elif header == 'Adreso eilutė 2':
            return address2 + ' ' + address3
        else:
            return ''


if __name__ == "__main__":
    pass