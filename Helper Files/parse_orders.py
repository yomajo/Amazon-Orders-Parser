from amzn_parser_constants import DPOST_HEADERS, DPOST_HEADERS_MAPPING, DPOST_FIXED_VALUES
from amzn_parser_utils import get_origin_country, get_product_category, get_level_up_abspath, get_total_price
from etonas_xlsx_exporter import EtonasExporter
from datetime import datetime
import logging
import sys
import csv
import os


# GLOBAL VARIABLES
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'
VBA_NO_NEW_JOB = 'NO NEW JOB'
VBA_KEYERROR_ALERT = 'ERROR_IN_SOURCE_HEADERS'
VBA_DPOST_CHARTLIMIT_ALERT = 'DPOST_CHARLIMIT_WARNING'
DPOST_REF_CHARLIMIT_PER_CELL = 28


class ParseOrders():
    '''Input: orders as list of dicts, outputs csv, xlsx files based on shipment method'''
    
    def __init__(self, all_orders : list):
        self.all_orders = all_orders
        self.dpost_orders = []
        self.etonas_orders = []
        self.ups_orders = []
    
    def export_same_buyer_details(self):
        '''exports orders data made by same person'''
        same_buyer_orders = self.get_same_buyer_orders()
        if not same_buyer_orders:
            logging.info(f'No orders by same person in this batch. Skipping export to txt')
            return
        with open(self.same_buyers_filename, 'w', encoding='utf-8') as f:
            f.write('Buyer\t\tOrder Number\t\t\tShipping Address(1-2)')
            for recipient_name in same_buyer_orders:
                f.write(f'\n\n{recipient_name}')
                for order in same_buyer_orders[recipient_name]:
                    f.write(f"\n\t\t{order['order-id']}\t\t{order['ship-address-1']} {order['ship-address-2']}")
        logging.info(f'Same Buyer Orders have been written to {self.same_buyers_filename} and being showed to client')
        os.startfile(self.same_buyers_filename)

    def get_same_buyer_orders(self):
        '''step1: collects {recipient-name: [{order1 details}, {order2 details}]} structure; step2: removes single orders'''
        recipient_name_keys_orders = {}
        for order_details in self.all_orders:
            # If name is in same_buyers_orders keys, append order dict as list item, else, add order dict as list
            if order_details['recipient-name'] in recipient_name_keys_orders:
                recipient_name_keys_orders[order_details['recipient-name']].append(order_details)
            else:
                recipient_name_keys_orders[order_details['recipient-name']] = [order_details]
        # Filter for same person orders dict, where key is recipient name and value is a list of order dicts:
        for name_key in list(recipient_name_keys_orders):
            if len(recipient_name_keys_orders[name_key]) == 1:
                recipient_name_keys_orders.pop(name_key, None)
        return recipient_name_keys_orders

    def export_csv(self, csv_filename : str, headers : list, contents : list):
        try:
            with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as csv_f:
                writer = csv.DictWriter(csv_f, fieldnames=headers, delimiter=';')
                writer.writeheader()
                writer.writerows(contents)
        except Exception as e:
            logging.error(f'Error occured while exporting data to csv. Error: {e}.Arguments:\nheaders: {headers}\ncontents: {contents}')

    def reformat_data_to_dpost_output(self, orders_data : list):
        '''reduces input data to that needed in output csv'''
        try:
            dpost_ready_data = []
            for order_dict in orders_data:
                reduced_order_dict = self.prepare_dpost_order_contents(order_dict)
                dpost_ready_data.append(reduced_order_dict)
            return dpost_ready_data
        except Exception as e:
            print(VBA_ERROR_ALERT)
            logging.critical(f'Error while iterating collected row dicts and trying to reduce. Error: {e}')

    def prepare_dpost_order_contents(self, order_dict : dict):
        d_with_output_keys = {}
        for header in DPOST_HEADERS:
            if header in DPOST_FIXED_VALUES.keys():
                d_with_output_keys[header] = DPOST_FIXED_VALUES[header]
            elif header in DPOST_HEADERS_MAPPING.keys():
                d_with_output_keys[header] = order_dict[DPOST_HEADERS_MAPPING[header]]
                # warn in VBA if char limit per cell is exceeded in DPost reference column
                if 'cust_ref' in header.lower() and len(d_with_output_keys[header]) > DPOST_REF_CHARLIMIT_PER_CELL:
                    logging.info(f'Order with key {header} and value {d_with_output_keys[header]} triggered VBA warning for charlimit in DPost')
                    print(VBA_DPOST_CHARTLIMIT_ALERT)
            elif header == 'DETAILED_CONTENT_DESCRIPTIONS_1':
                d_with_output_keys[header] = get_product_category(order_dict['product-name'])
            elif header in ['DECLARED_VALUE_1', 'TOTAL_VALUE']:
                d_with_output_keys[header] = get_total_price(order_dict)
            elif header == 'DECLARED_ORIGIN_COUNTRY_1':
                d_with_output_keys[header] = get_origin_country(order_dict['product-name'])
            else:
                d_with_output_keys[header] = ''
        return d_with_output_keys
    
    def sort_orders_by_shipment_company(self):
        '''sorts orders by shipment company. Performs check in the end for empty lists'''    
        for order in self.all_orders:
            if self._get_order_ship_country(order) in ['GB', 'UK']:
                self.etonas_orders.append(order)
            elif self._get_order_ship_price(order) >= 10:
                self.ups_orders.append(order)
            else:
                self.dpost_orders.append(order)
        self.exit_no_new_orders()
    
    def exit_no_new_orders(self):
        if not self.etonas_orders and not self.dpost_orders and not self.ups_orders:
            logging.info(f'No new orders for processing provided with filtering oder ID (see log above). Terminating, alerting VBA.')
            print(VBA_NO_NEW_JOB)
            sys.exit()

    @staticmethod
    def _get_order_ship_price(order):
        try:
            return float(order['shipping-price'])
        except KeyError:
            logging.critical(f'Could not find column: \'shipping-price\' in data source. Exiting on order: {order}')
            print(VBA_KEYERROR_ALERT)
            sys.exit()
        except Exception as e:
            logging.warning(f'Error retrieving shipping-price in order: {order}, returning 0 (integer). Error: {e}')
            return 0
    
    @staticmethod
    def _get_order_ship_country(order):
        try:
            return order['ship-country'].upper()
        except KeyError:
            logging.critical(f'Could not find column: \'ship-country\' in data source. Exiting on order: {order}')
            print(VBA_KEYERROR_ALERT)
            sys.exit()
        except Exception as e:
            logging.warning(f'Error retrieving ship-country in order: {order}, returning empty string. Error: {e}')
            return ''

    def prepare_filepaths(self):
        '''creates cls variables of files abs paths to be created one dir above this script dir'''
        curr_folder = os.path.dirname(os.path.abspath(__file__))
        parent_dir = get_level_up_abspath(curr_folder)
        date_stamp = datetime.today().strftime("%Y.%m.%d %H.%M")
        self.same_buyers_filename = os.path.join(parent_dir, f'Same Buyer Orders {date_stamp}.txt')
        self.etonas_filename = os.path.join(parent_dir, f'Etonas-Amazon {date_stamp}.xlsx')
        self.dpost_filename = os.path.join(parent_dir, f'DPost-Amazon {date_stamp}.csv')
        self.ups_filename = os.path.join(parent_dir, f'UPS-Amazon {date_stamp}.csv')

    def export_dpost(self):
        if self.dpost_orders:
            dpost_content = self.reformat_data_to_dpost_output(self.dpost_orders)
            self.export_csv(self.dpost_filename, DPOST_HEADERS, dpost_content)
            logging.info(f'CSV {self.dpost_filename} created. Orders inside: {len(self.dpost_orders)}')

    def export_ups(self):
        if self.ups_orders:
            ups_content = self.reformat_data_to_dpost_output(self.ups_orders)
            self.export_csv(self.ups_filename, DPOST_HEADERS, ups_content)
            logging.info(f'CSV {self.ups_filename} created. Orders inside: {len(self.ups_orders)}')

    def export_etonas(self):
        if self.etonas_orders:
            EtonasExporter(self.etonas_orders, self.etonas_filename).export()
            logging.info(f'XLSX {self.etonas_filename} created. Orders inside: {len(self.etonas_orders)}')

    def export_orders(self, testing=False):
        '''Summing up tasks inside ParseOrders class'''
        self.prepare_filepaths()
        self.sort_orders_by_shipment_company()
        self.export_same_buyer_details()
        if testing:
            logging.info(f'Suspended export of orders due to flag testing value: {testing}')
            print(f'Suspended export of orders due to flag testing value: {testing}')
            return
        self.export_dpost()
        self.export_ups()
        self.export_etonas()

if __name__ == "__main__":
    pass