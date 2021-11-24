from parser_utils import get_origin_country, get_total_price, get_sales_channel_hs_code
from parser_constants import ETONAS_HEADERS, ETONAS_HEADERS_MAPPING
from parser_constants import NLPOST_HEADERS, NLPOST_HEADERS_MAPPING, NLPOST_FIXED_VALUES
import logging
import openpyxl
import sys


# to do:
# 1. add validation to mirror vba side
# 2. functions to add certain data column values
# 3. rewrite category from batteries to alkaline batteries
# unmapped nl headers:
'''
    'Receiver phone' : '',
    'Receiver email' : '',
    'Receiver street' : '',
    'Service name' : '',
    'HS code' : '',
''' 


# GLOBAL VARIABLES
ETONAS_CHARLIMIT_PER_CELL = 32
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'
VBA_ETONAS_CHARTLIMIT_ALERT = 'ETONAS_CHARLIMIT_WARNING'
HEADER_SETTINGS = {'etonas': {'headers' : ETONAS_HEADERS, 'mapping': ETONAS_HEADERS_MAPPING}, 
                'nlpost': {'headers' : NLPOST_HEADERS, 'mapping': NLPOST_HEADERS_MAPPING, 'fixed': NLPOST_FIXED_VALUES}}


class XlsxExporter():
    '''generic class for creating workbook based on Etonas/NLPost shippment companies xlsx requirements.
    Assumes class that inherit this class have appropriate names as part of class name: (Etonas* / NLPost*)
    
    Args:
    -input_orders: list of orders (dicts) as accepted by class
    -export_path: workbook path to be saved at
    -sales_channel: str option AmazonEU / AmazonCOM / Etsy
    -proxy_keys: dict to handle both Amazon and Etsy sales channels'''

    def __init__(self, input_orders : list, export_path : str, sales_channel : str, proxy_keys : dict):
        self.input_orders = input_orders
        self.export_path = export_path
        self.sales_channel = sales_channel
        self.proxy_keys = proxy_keys
        self.__get_mode()
        self.header_settings = HEADER_SETTINGS[self.mode]
        self.row_offset = 1 if self.mode == 'nlpost' else 0

    def __get_mode(self):
        '''sets self.mode variable to differentiate Etonas / NLPost workbook generation'''
        self.mode = 'etonas' if self.__class__.__name__.startswith('Etonas') else 'nlpost'
        logging.debug(f'{self.mode}')


    def refactor_data_for_export(self):
        '''reduces input data to that needed in output xlsx'''
        try:
            export_ready_data = []
            for order in self.input_orders:
                reduced_order = self._refactor_order(order)
                export_ready_data.append(reduced_order)
            return export_ready_data
        except Exception as e:
            print(VBA_ERROR_ALERT)
            logging.warning(f'Error while iterating collected row dicts and trying to reduce in XlsxExporter mode: {self.mode}. Error: {e}')

    def _refactor_order(self, order:dict) -> dict:
        '''refactors order based on self.mode via prepare_etonas_order_contents or prepare_nlpost_order_contents methods'''
        if self.mode == 'etonas':
            reduced_order = self.prepare_etonas_order_contents(order)
        else:
            reduced_order = self.prepare_nlpost_order_contents(order)
        return reduced_order

    def prepare_etonas_order_contents(self, order:dict) -> dict:
        '''implemented in inheriting class'''
        logging.warning(f'You should not be using generic class to create xlsx output. Warning from: prepare_etonas_order_contents method')
        return order
    
    def prepare_nlpost_order_contents(self, order:dict) -> dict:
        '''implemented in inheriting class'''
        logging.warning(f'You should not be using generic class to create xlsx output. Warning from: prepare_nlpost_order_contents method')
        return order

    def _get_fname_lname(self, order:dict):
        '''returns first and last name based on sales channel'''
        try:
            if self.sales_channel == 'Etsy':
                f_name = order[self.proxy_keys['buyer-fname']]
                l_name = order[self.proxy_keys['buyer-lname']]
                return f_name, l_name
            else:
                f_name, l_name = order[self.proxy_keys['recipient-name']].split(' ', 1)
                return f_name, l_name
        except KeyError as e:
            logging.critical(f'No recipient-name key for etonas func: _get_fname_lname. Err: {e} Order: {order}')
            print(VBA_ERROR_ALERT)
            sys.exit()
        except ValueError as e:
            logging.debug(f'Failed to unpack f_name, l_name for sales ch: {self.sales_channel} etonas xlsx. Err: {e}. Returning proxy recipient-name order val: {order[self.proxy_keys["recipient-name"]]} and empty l_name')
            return order[self.proxy_keys['recipient-name']], ''

    def __get_weight_in_kg(self, order:dict):
        '''returns order weight in kg if possible, empty str if not'''
        try:
            return round(order['weight'] / 1000, 2)
        except:
            return ''

    def _write_headers(self, ws:object, headers:list):
        for col, header in enumerate(headers, 1):
            ws.cell(1 + self.row_offset, col).value = header    

    @staticmethod
    def range_generator(orders:list, headers:list):
        for row, _ in enumerate(orders):
            for col, _ in enumerate(headers):
                yield row, col
    
    def _write_orders(self, ws:object, headers:list, orders:list):
        for row, col in self.range_generator(orders, headers):
            working_dict = orders[row]
            key_pointer = headers[col]
            # offsets due to excel vs python numbering  + headers in row 1 + self.row_offset (first empty row for nlpost)
            ws.cell(row + 2 + self.row_offset, col + 1).value = working_dict[key_pointer]

    def adjust_col_widths(self, ws:object):
        '''iterates cols, cells within col, adjusts column width based on max char cell within col + extra spacing'''
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.1
            ws.column_dimensions[col_letter].width = adjusted_width

    def export(self):
        export_data = self.refactor_data_for_export()
        wb = openpyxl.Workbook()
        ws = wb.active
        headers = self.header_settings['headers']
        self._write_headers(ws, headers)
        self._write_orders(ws, headers, export_data)
        self.adjust_col_widths(ws)
        wb.save(self.export_path)
        wb.close()


class NLPostExporter(XlsxExporter):
    '''Creates Excel orders workbook based on NLPost xlsx requirements. Uses generic parent XlsxExporter class. 
    class name must include word 'NLPost' (not actually, but kepping it clean).
    
    only overwritten method: prepare_nlpost_order_contents
    
    Args:
    -input_orders: list of orders (dicts) as accepted by class
    -export_path: workbook path to be saved at
    -sales_channel: str option AmazonEU / AmazonCOM / Etsy
    -proxy_keys: dict to handle both Amazon and Etsy sales channels'''

    def prepare_nlpost_order_contents(self, order:dict) -> dict:
        '''returns ready-to-write order data dict based on NLPost file headers'''
        export = {}
        return order


class EtonasExporter(XlsxExporter):
    '''Creates Excel orders workbook based on Etonas xlsx requirements. Uses generic parent XlsxExporter class. 
    class name must include word 'Etonas'.
    
    only overwritten method: prepare_etonas_order_contents
    
    Args:
    -input_orders: list of orders (dicts) as accepted by class
    -export_path: workbook path to be saved at
    -sales_channel: str option AmazonEU / AmazonCOM / Etsy
    -proxy_keys: dict to handle both Amazon and Etsy sales channels'''


    def prepare_etonas_order_contents(self, order:dict) -> dict:
        '''returns ready-to-write order data dict based on Etonas file headers'''
        export = {}
        first_name, last_name = self._get_fname_lname(order)
        
        # #####################################################################
        # change here to proxy key: title
        product_name_proxy_key = self.proxy_keys.get('product-name', '')
        # #####################################################################

        # Change GB to UK for Etonas
        if order[self.proxy_keys['ship-country']] == 'GB':
            order[self.proxy_keys['ship-country']] = 'UK'
        
        for header in ETONAS_HEADERS:
            if header in ETONAS_HEADERS_MAPPING.keys():
                # Etsy has no phone, email, returning empty string, to prevent KeyError
                target_key = self.proxy_keys.get(ETONAS_HEADERS_MAPPING[header], '')
                export[header] = order.get(target_key, '')

                # warn in VBA if char limit per cell is exceeded in Etonas address lines 1/2/3/4
                if 'address' in header.lower() and len(export[header]) > ETONAS_CHARLIMIT_PER_CELL:
                    logging.info(f'Order with key {header} and value {export[header]} triggered VBA warning for charlimit set by Etonas')
                    print(VBA_ETONAS_CHARTLIMIT_ALERT)
            
            elif header == 'First_name':
                export[header] = first_name
            elif header == 'Last_name':
                export[header] = last_name
            elif header == 'HS':
                export[header] = get_sales_channel_hs_code(order, product_name_proxy_key)
            elif header == 'Origin':
                # etsy - no item title, hardcoding for etsy until weight mapping
                if product_name_proxy_key == '':
                    export[header] = 'CN'
                else:
                    export[header] = get_origin_country(order[product_name_proxy_key])
            elif header == 'Currency':
                target_key = self.proxy_keys['currency']
                export[header] = order[target_key].lower()
            elif header == 'Price per quantity':
                export[header] = get_total_price(order, self.sales_channel)
            elif header == 'Weight(Kg)':
                export[header] = self.__get_weight_in_kg(order)
            else:
                export[header] = ''
        return export


if __name__ == "__main__":
    # etonas = NLPostExporter([], '', '', {})
    pass