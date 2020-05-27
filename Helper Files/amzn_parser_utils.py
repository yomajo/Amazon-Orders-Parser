from amzn_parser_constants import ORIGIN_COUNTRY_CRITERIAS, CATEGORY_CRITERIAS
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

def get_output_dir():
    '''returns target dir for output files depending on execution type (.exe/.py)'''
    # pyinstaller sets 'frozen' attr to sys module when compiling
    if getattr(sys, 'frozen', False):
        curr_folder = os.path.dirname(sys.executable)
    else:
        curr_folder = os.path.dirname(os.path.abspath(__file__))
    return get_level_up_abspath(curr_folder)


if __name__ == "__main__":
    pass