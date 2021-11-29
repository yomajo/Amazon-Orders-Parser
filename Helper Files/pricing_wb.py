from file_utils import get_output_dir
from excel_utils import get_last_used_row_col, cell_to_float
import openpyxl
import logging
import os
from countries import COUNTRY_CODES

# while developing:
log_path = os.path.join(get_output_dir(client_file=False), 'temp.log')
logging.basicConfig(handlers=[logging.FileHandler(log_path, 'a', 'utf-8')], level=logging.DEBUG)
from parser_constants import AMAZON_KEYS

# GLOBAL VARIABLES
PRICING_WB = 'PRICING.xlsx'
ALLOWED_SERVICE_QUERIES = ['NL', 'LP', 'DP', 'ETONAS', 'DPD', 'UPS']


class PricingWB:
    '''interaction with PRICING.xlsx workbook. Assumes integrity has been checked in VBA side.
    
    main method:
    
    '''

    def __init__(self, proxy_keys:dict):
        self.proxy_keys = proxy_keys
        wb_path = os.path.join(get_output_dir(client_file=False), PRICING_WB)
        self.wb = openpyxl.load_workbook(wb_path)
        self.ws_tracked = self.wb['PrTracked']
        self.ws_untracked = self.wb['PrUntracked']
        self.ws_tracked_limits = get_last_used_row_col(self.ws_tracked)
        self.ws_untracked_limits = get_last_used_row_col(self.ws_untracked)

    def get_pricing_offer(self, order:dict, service:str):
        '''returns price offer for order data provided. External error handling, allow to fail here'''
        tracked,  weight, vmdoption, country_code = order['tracked'], order['weight'], order['vmdoption'], order[self.proxy_keys['ship-country']]
        self.__validate_query(service, country_code)
        ws = self.ws_tracked if tracked else self.ws_untracked
        limits = self.ws_tracked_limits if tracked else self.ws_untracked_limits
        target_row = self.__get_country_row(ws, limits, country_code)
        print(f'{country_code} found in tracked: {tracked} sheet row: {target_row}')

        offer = ''
        return cell_to_float(offer)


    def __validate_query(self, service:str, country_code:str):
        '''validates external querying for basic compatibility with pricing sheets'''
        if service not in ALLOWED_SERVICE_QUERIES:
            logging.critical(f'Pricing was queried by unsupported service: {service}')
            raise ValueError('Order pricing: Service not supported')
        if country_code not in COUNTRY_CODES.values():
            logging.warning(f'Attempt to query pricing for not supported country: {country_code}')
            raise ValueError('Order pricing: Country code not supported')

    def __get_country_row(self, ws:object, limits:dict, country_code:str) -> int:
        '''returns country matching row inside ws sheet. 0 if not found'''
        max_row = limits['max_row']
        for row in range(1, max_row + 1):
            if ws.cell(row=row, column=1).value == country_code:                
                return row
        return 0


def test():
    order = {'vmdoption':'MKS', 'weight':246.9, 'tracked':True, 'ship-country':'NL'}
    pricing = PricingWB(AMAZON_KEYS)
    etonas_offer = pricing.get_pricing_offer(order, service='ETONAS')


if __name__ == '__main__':
    test()
    # pass