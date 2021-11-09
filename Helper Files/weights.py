from parser_constants import AMAZON_KEYS, ETSY_KEYS, QUANTITY_PATTERN
from excel_utils import get_last_used_row_col, cell_to_float
from file_utils import get_output_dir, read_json_to_obj, dump_to_json
from parser_utils import get_inner_qty_sku, get_product_category_or_brand
import openpyxl
import logging
import os

# GLOBAL VARIABLES
WB_NAME = 'WEIGHTS.xlsx'
WEIGHT_WB_PATH = os.path.join(get_output_dir(client_file=False), WB_NAME)


class OrderData():
    '''adds data to each order in passed orders list. Class assumes workbook WEIGHTS.xlsx is in Helper Files folder
    and its data integrity, fixed headers are in place. Main method:

    add_orders_data() - adds category, brand, mksdksoption, weight to order dict keys
    
    Arguments:
    orders: list of order dicts
    sales_channel: str
    proxy_keys: dict'''

    def __init__(self, orders:list, sales_channel:str, proxy_keys:dict):
        self.orders = orders
        self.sales_channel = sales_channel
        self.proxy_keys = proxy_keys
        
        self.weight_data = self._parse_weights_wb()
        self.pattern = QUANTITY_PATTERN[sales_channel]

        self.no_matching_skus = []
        self.invalid_orders = 0    

    def _parse_weights_wb(self) -> dict:
        '''returns weights data as dict from reading excel workbook'''
        ws = self._get_weight_ws()
        ws_limits = get_last_used_row_col(ws)
        weight_data = self._get_ws_data(ws, ws_limits)
        self.wb.close()
        return weight_data

    def _get_weight_ws(self):
        '''returns ws object'''
        self.wb = openpyxl.load_workbook(WEIGHT_WB_PATH)
        ws = self.wb['Weight']
        return ws
    
    def _get_ws_data(self, ws:object, ws_limits:dict) -> dict:
        '''returns worksheet data as list of dicts, with keys corresponding to header data'''
        ws_data = {}
        max_row = ws_limits['max_row']
        max_col = ws_limits['max_col']
        for r in range(2, max_row + 1):
            row_data = {}
            for c in range(2, max_col + 1):
                header = ws.cell(row=1, column=c).value
                cell_value = cell_to_float(ws.cell(row=r, column=c).value)
                row_data[header] = cell_value
            ws_data[ws.cell(row=r, column=1).value] = row_data
        return ws_data

    def __get_order_quantity(self, order:dict) -> int:
        '''returns 'quantity-purchased' order key value in integer form'''
        return int(order[self.proxy_keys['quantity-purchased']])


    def add_orders_data(self) -> list:
        '''adds properties to each order (keys):
        -weight (order weight as float)
        -mksdksoption (string)
        -brand (string)
        -category (string)'''
        
        for order in self.orders:
            qty_purchased = self.__get_order_quantity(order)
            skus = order[self.proxy_keys['sku']]

            # Add brand / category data to order, using first item in sku list
            order = self._add_order_brand_category_data(order, skus)

            if self._validate_calculation(qty_purchased, skus):
                order = self._calc_weight_add_data(order, qty_purchased, skus)
            else:
                order = self._add_invalid_weight_data(order)
        
        percentage_invalid = self.invalid_orders / len(self.orders) * 100
        logging.info(f'{percentage_invalid:.2f}% orders contain SKU\'s that are invalid for weight calculation')
        return self.orders
    
    def _add_order_brand_category_data(self, order:dict, skus:list) -> dict:
        '''returns order w/ added brand, category keys (title possibly for etsy based on first sku in order)'''
        if self.sales_channel == 'Etsy':
            order = self._add_etsy_order_title(order, skus)
        title = order[self.proxy_keys['title']]
        order['brand'] = get_product_category_or_brand(title, return_brand=True)
        order['category'] = get_product_category_or_brand(title, return_brand=False)
        return order

    def _add_etsy_order_title(self, order:dict, skus:list) -> dict:
        '''adds Etsy order title to order dict'''
        for sku in skus:
            _, inner_sku = get_inner_qty_sku(sku, self.pattern)
            sku_weight_data = self.weight_data[inner_sku]
            title = sku_weight_data['Title']
            if title:
                order['title'] = title
                logging.debug(f'Adding title to etsy order: {title} based on inner sku: {inner_sku}')
                return order
        # no valid title found
        order['title'] = 'Title not available'
        return order

    def _validate_calculation(self, qty_purchased:int, skus:list) -> bool:
        '''returns False if: for Etsy orders, when weight can not be calculated due to various possible combinations'''
        if self.sales_channel == 'Etsy':
            if len(skus) > 1 and qty_purchased != len(skus):
                logging.debug(f'Etsy order weights can\'t be calculated due to various possible combinations. Qty: {qty_purchased}, skus: {skus}')
                return False
        return True

    def _calc_weight_add_data(self, order:dict, qty_purchased:int, skus:list) -> dict:
        '''adds weight related data to order dict'''
        order_weight = 0.0
        package_weight = 0.0
        self.mksdksoption = ''
        try:
            for sku in skus:
                inner_qty, inner_sku = get_inner_qty_sku(sku, self.pattern)

                sku_weight_data = self.weight_data[inner_sku]
                sku_weight = float(sku_weight_data['Weight'])
                order_sku_weight = sku_weight * inner_qty
                
                # multuply with external order quantity only when order contains single sku
                if len(skus) == 1:
                    order_weight += order_sku_weight * qty_purchased
                else:
                    order_weight += order_sku_weight

                potential_package_weight = float(self._get_potential_package_weight(order, sku_weight_data))
                # update package weight if sku package weight is > current package weight
                if potential_package_weight > package_weight:
                    package_weight = potential_package_weight
                
                self._update_mksdksoption(sku_weight_data)

            order_weight += package_weight
            order['weight'] = order_weight
            order['mksdksoption'] = self.mksdksoption
            return order
        except:
            return self._add_invalid_weight_data(order)

    def _get_potential_package_weight(self, order:dict, sku_weight_data:dict) -> float:
        '''returns package weight as float based on product category'''
        try:
            if order['category'] =='PLAYING CARDS' or order['category'] =='TAROT CARDS':
                return float(sku_weight_data['Package DP'])
            else:
                return float(sku_weight_data['Package LP'])
        except:
            # to fail float casting in _calc_weight_add_data
            return 'No package weight available'
    
    def _update_mksdksoption(self, sku_weight_data:dict):
        '''updates self.mksdksoption for order'''
        potential_option = sku_weight_data['MKS/DKS']
        if potential_option in ['MKS', 'DKS']:
            if self.mksdksoption == '':
                # self.mksdksoption is not set (first sku in order)
                self.mksdksoption = potential_option
            elif self.mksdksoption == 'MKS' and potential_option == 'DKS':
                # upgrade to DKS if current option is MKS
                self.mksdksoption = potential_option


    def _add_invalid_weight_data(self, order:dict) -> dict:
        '''adds invalid weight data to order dict'''
        self.invalid_orders += 1
        logging.debug(f'order: {order[self.proxy_keys["order-id"]]} cant calc weights. skus: {order[self.proxy_keys["sku"]]}')

        self.no_matching_skus.append(order[self.proxy_keys['sku']])

        order['weight'] = ''
        order['mksdksoption'] = ''
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
    order_metadata = OrderData(orders, sales_channel, proxy_keys)
    orders_with_weights = order_metadata.add_orders_data()
    order_metadata.export_target_data('Etsy_orders_with_weights.json')



if __name__ == '__main__':
    # run()
    pass