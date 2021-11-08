from parser_constants import AMAZON_KEYS, ETSY_KEYS, QUANTITY_PATTERN
from excel_utils import get_last_used_row_col, cell_to_float
from file_utils import get_output_dir, read_json_to_obj, dump_to_json
from parser_utils import get_inner_qty_sku, split_sku
import openpyxl
import logging
import os

# GLOBAL VARIABLES
WB_NAME = 'WEIGHTS.xlsx'
WEIGHT_WB_PATH = os.path.join(get_output_dir(client_file=False), WB_NAME)


class Weights():
    ''''''

    def __init__(self, orders:list, sales_channel:str, proxy_keys:dict):
        self.orders = orders
        self.sales_channel = sales_channel
        self.proxy_keys = proxy_keys
        self.ws = self._get_weight_ws()
        self.ws_limits = get_last_used_row_col(self.ws)
        self.weight_data = self._get_ws_data()
        self.wb.close()
        self.pattern = QUANTITY_PATTERN[sales_channel]        
        self.no_matching_skus = []
        self.invalid_orders = 0    

    def _get_weight_ws(self):
        '''returns ws object'''
        self.wb = openpyxl.load_workbook(WEIGHT_WB_PATH)
        ws = self.wb['Weight']
        return ws
    
    def _get_ws_data(self):
        '''returns worksheet data as list of dicts, with keys corresponding to header data'''
        ws_data = {}
        max_row = self.ws_limits['max_row']
        max_col = self.ws_limits['max_col']
        for r in range(2, max_row + 1):
            row_data = {}
            for c in range(2, max_col + 1):
                header = self.ws.cell(row=1, column=c).value
                cell_value = cell_to_float(self.ws.cell(row=r, column=c).value)
                row_data[header] = cell_value
            ws_data[self.ws.cell(row=r, column=1).value] = row_data
        return ws_data

    def __get_order_quantity(self, order:dict) -> int:
        '''returns 'quantity-purchased' order key value in integer form'''
        return int(order[self.proxy_keys['quantity-purchased']])


    def add_weights(self) -> list:
        '''attempts to calculate and add weight data to order dicts'''
        for order in self.orders:
            qty_purchased = self.__get_order_quantity(order)
            skus = order[self.proxy_keys['sku']]
            
            # delete later
            order_id = order[self.proxy_keys['order-id']]

            if self._validate_calculation(qty_purchased, skus):
                order = self._calc_weight_add_data(order, qty_purchased, skus)
            else:
                order = self._add_invalid_weight_data(order)
        percentage_invalid = self.invalid_orders / len(self.orders) * 100
        logging.info(f'{percentage_invalid:.2f}% orders contain SKU\'s that are invalid for weight calculation')
        return self.orders
    
    def _validate_calculation(self, qty_purchased:int, skus:list) -> bool:
        '''returns False if: for Etsy orders, when weight can not be calculated due to various possible combinations'''
        if self.sales_channel == 'Etsy':
            if len(skus) >= 2 and qty_purchased != len(skus):
                logging.debug(f'Etsy order weights can\'t be calculated due to various possible combinations. Qty: {qty_purchased}, skus: {skus}')
                self.invalid_orders += 1
                return False
        return True

    def _calc_weight_add_data(self, order:dict, qty_purchased:int, skus:list) -> dict:
        '''adds weight related data to order dict'''
        order_weight = 0.0
        package_weight = 0.0
        try:
            for sku in skus:
                potential_package_weight = 0.0
                inner_qty, inner_sku = get_inner_qty_sku(sku, self.pattern)

                sku_weight_data = self.weight_data[inner_sku]
                sku_weight = float(sku_weight_data['Weight'])
                order_sku_weight = sku_weight * inner_qty
                order_weight += order_sku_weight * qty_purchased

                potential_package_weight = float(sku_weight_data['Package LP'])
                # update package weight if sku package weight is > current package weight
                if potential_package_weight > package_weight:
                    package_weight = potential_package_weight
            
            order_weight += package_weight
            order['weight'] = order_weight
            order['MKSDKSOption'] = 'HARDCODED'
            return order
        except:
            self.invalid_orders += 1
            return self._add_invalid_weight_data(order)


    def _add_invalid_weight_data(self, order:dict) -> dict:
        '''adds invalid weight data to order dict'''
        logging.debug(f'order: {order[self.proxy_keys["order-id"]]} cant calc weights. skus: {order[self.proxy_keys["sku"]]}')

        self.no_matching_skus.append(order[self.proxy_keys['sku']])

        order['weight'] = ''
        order['MKSDKSOption'] = ''
        return order
    
    def export_target_data(self, json_filename:str):
        '''exports target data to json file'''
        target_data = {
            'orders': self.orders,
            'no_matching_skus': self.no_matching_skus
        }
        dump_to_json(target_data, json_filename)


def run():
    sales_channel = 'Etsy'
    proxy_keys = ETSY_KEYS if sales_channel == 'Etsy' else AMAZON_KEYS
    TEST_ORDERS_JSON = 'Etsy_orders.json' if sales_channel == 'Etsy' else 'AmazonEU_orders.json'
    orders = read_json_to_obj(TEST_ORDERS_JSON)
    # inspect_sku(orders)
    weights = Weights(orders, sales_channel, proxy_keys)
    orders_with_weights = weights.add_weights()
    weights.export_target_data('Etsy_orders_with_weights.json')



if __name__ == '__main__':
    # run()
    pass