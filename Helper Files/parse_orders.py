from amzn_parser_utils import get_origin_country, get_product_category, get_level_up_abspath, get_total_price, get_output_dir
from amzn_parser_constants import DPOST_HEADERS, DPOST_HEADERS_MAPPING, DPOST_FIXED_VALUES
from etonas_xlsx_exporter import EtonasExporter
from string import ascii_letters
from datetime import datetime
import logging
import sys
import csv
import os


# GLOBAL VARIABLES
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'
VBA_NO_NEW_JOB = 'NO NEW JOB'
VBA_KEYERROR_ALERT = 'ERROR_IN_SOURCE_HEADERS'
VBA_DPOST_CHARLIMIT_ALERT = 'DPOST_CHARLIMIT_WARNING'
DPOST_NAME_CHARLIMIT = 30
DPOST_ADDRESS_CHARLIMIT = 40


class ParseOrders():
    '''Input: orders as list of dicts, outputs csv, xlsx files based on shipment method
    
    export_orders(testing=False) : main method, sorts orders by shipment company, if testing flag is False,
    exports files with appropriate orders data and adds all passed orders when creating class to database'''
    
    def __init__(self, all_orders : list, db_client : object):
        self.all_orders = all_orders
        self.db_client = db_client
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
                validated_order_dict = self.__validate_dpost_order(reduced_order_dict)
                dpost_ready_data.append(validated_order_dict)
            return dpost_ready_data
        except Exception as e:
            print(VBA_ERROR_ALERT)
            logging.critical(f'Error while iterating collected row dicts and trying to reduce. Error: {e}')

    def prepare_dpost_order_contents(self, order_dict : dict):
        '''outputs a dir, those keys correspong to target csv headers'''        
        d_with_output_keys = {}
        for header in DPOST_HEADERS:
            if header in DPOST_FIXED_VALUES.keys():
                d_with_output_keys[header] = DPOST_FIXED_VALUES[header]
            elif header in DPOST_HEADERS_MAPPING.keys():
                d_with_output_keys[header] = order_dict[DPOST_HEADERS_MAPPING[header]]
            elif header == 'DETAILED_CONTENT_DESCRIPTIONS_1':
                d_with_output_keys[header] = get_product_category(order_dict['product-name'])
            elif header in ['DECLARED_VALUE_1', 'TOTAL_VALUE']:
                d_with_output_keys[header] = get_total_price(order_dict)
            elif header == 'DECLARED_ORIGIN_COUNTRY_1':
                d_with_output_keys[header] = get_origin_country(order_dict['product-name'])
            elif header == 'CUST_REF':
                d_with_output_keys[header] = order_dict['recipient-name'][:20]
            else:
                d_with_output_keys[header] = ''
        return d_with_output_keys

    def __validate_dpost_order(self, order_dict : dict) -> dict:
        '''rearranges /shortens data fields on demand (charlimit for fields)
        Takes care of: address1,2,3 , name, postcode fields'''
        name = order_dict['NAME']
        order_dict['POSTAL_CODE'] = order_dict['POSTAL_CODE'].upper()

        if len(name) > DPOST_NAME_CHARLIMIT:
            logging.debug('Order enters name shortening functions')
            order_dict['NAME'] = self.__shorten_word_sequence(name)

        if len(order_dict['ADDRESS_LINE_1']) > DPOST_ADDRESS_CHARLIMIT or \
            len(order_dict['ADDRESS_LINE_2']) > DPOST_ADDRESS_CHARLIMIT or \
            len(order_dict['ADDRESS_LINE_3']) > DPOST_ADDRESS_CHARLIMIT:
            logging.debug('Order enters address reorganisation')
            order_dict = self.__reorg_dpost_order_addr(order_dict)        
        return order_dict
    
    def __shorten_word_sequence(self, long_seq : str) -> str:
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
                    abbr_word = self.__abbreviate_word(word)
                    shortened_seq_lst.append(abbr_word)
            short_seq = ' '.join(shortened_seq_lst)
            assert len(short_seq) <= DPOST_NAME_CHARLIMIT, 'Shortened name did not pass charlimit validation'
            return short_seq        
        except Exception as e:
            logging.warning(f'Could not shorten name: {long_seq}. Error: {e}. Alerting VBA, returning unedited')
            print(VBA_DPOST_CHARLIMIT_ALERT)
            return long_seq

    @staticmethod
    def __abbreviate_word(word : str) -> str:
        '''returns capitalized first letter with dot of provided word if it stars with letter'''            
        return word[0].upper() + '.' if word[0] in ascii_letters else word

    @staticmethod
    def __reorg_dpost_order_addr(order_dict : dict) -> dict:
        '''reoganizes address fields, returns original order dict, if reorganization still exceeds fields' limits'''
        original_order = order_dict.copy()
        logging.debug(f'Before address reorg:\nf1: {order_dict["ADDRESS_LINE_1"]}\nf2: {order_dict["ADDRESS_LINE_2"]}\nf3:{order_dict["ADDRESS_LINE_3"]}')
        total_address_seq = order_dict['ADDRESS_LINE_1'] + ' ' + order_dict['ADDRESS_LINE_2'] + ' ' + order_dict['ADDRESS_LINE_3']
        address_seq = total_address_seq.split()
        # Reset fields, declare availability flags
        order_dict['ADDRESS_LINE_1'] = order_dict['ADDRESS_LINE_2'] = order_dict['ADDRESS_LINE_3'] = ''
        f1_not_filled = f2_not_filled = True
        # Reorganizing fields
        for addr_item in address_seq:
            if len(order_dict['ADDRESS_LINE_1']) + len(addr_item) < DPOST_ADDRESS_CHARLIMIT and f1_not_filled:
                order_dict['ADDRESS_LINE_1'] = order_dict['ADDRESS_LINE_1'] + addr_item + ' '
            elif len(order_dict['ADDRESS_LINE_2']) + len(addr_item) < DPOST_ADDRESS_CHARLIMIT and f2_not_filled:
                order_dict['ADDRESS_LINE_2'] = order_dict['ADDRESS_LINE_2'] + addr_item + ' '
                f1_not_filled = False
            elif len(order_dict['ADDRESS_LINE_3']) + len(addr_item) < DPOST_ADDRESS_CHARLIMIT:
                order_dict['ADDRESS_LINE_3'] = order_dict['ADDRESS_LINE_3'] + addr_item + ' '
                f2_not_filled = False
            else:
                logging.warning(f'Address reorganization failed. Total address char count: {len(order_dict["ADDRESS_LINE_1"])+len(order_dict["ADDRESS_LINE_2"])+len(order_dict["ADDRESS_LINE_3"])} could not fit into 3x{DPOST_ADDRESS_CHARLIMIT}')
                logging.warning(f'Warning VBA, returning original order: {original_order}')
                print(VBA_DPOST_CHARLIMIT_ALERT)
                return original_order
        logging.debug(f'After reorg:\nf1: {order_dict["ADDRESS_LINE_1"]}\nf2: {order_dict["ADDRESS_LINE_2"]}\nf3:{order_dict["ADDRESS_LINE_3"]}')
        return order_dict

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
        '''terminates python program, closes db connection, warns VBA'''
        if not self.etonas_orders and not self.dpost_orders and not self.ups_orders:
            logging.info(f'No new orders for processing provided with filtering oder ID (see log above). Terminating, alerting VBA.')
            self.db_client.close_connection()
            print(VBA_NO_NEW_JOB)
            sys.exit()

    def _get_order_ship_price(self, order):
        try:
            return float(order['shipping-price'])
        except KeyError:
            logging.critical(f'Could not find column: \'shipping-price\' in data source. Exiting on order: {order}')
            self.db_client.close_connection()
            print(VBA_KEYERROR_ALERT)
            sys.exit()
        except Exception as e:
            logging.warning(f'Error retrieving shipping-price in order: {order}, returning 0 (integer). Error: {e}')
            return 0
    
    def _get_order_ship_country(self, order):
        try:
            return order['ship-country'].upper()
        except KeyError:
            logging.critical(f'Could not find column: \'ship-country\' in data source. Exiting on order: {order}')
            self.db_client.close_connection()
            print(VBA_KEYERROR_ALERT)
            sys.exit()
        except Exception as e:
            logging.warning(f'Error retrieving ship-country in order: {order}, returning empty string. Error: {e}')
            return ''

    def _prepare_filepaths(self):
        '''creates cls variables of files abs paths to be created one dir above this script dir'''
        output_dir = get_output_dir()
        date_stamp = datetime.today().strftime("%Y.%m.%d %H.%M")
        self.same_buyers_filename = os.path.join(output_dir, f'Same Buyer Orders {date_stamp}.txt')
        self.etonas_filename = os.path.join(output_dir, f'Etonas-Amazon {date_stamp}.xlsx')
        self.dpost_filename = os.path.join(output_dir, f'DPost-Amazon {date_stamp}.csv')
        self.ups_filename = os.path.join(output_dir, f'UPS-Amazon {date_stamp}.csv')

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
    
    def push_orders_to_db(self):
        '''adds all orders in this class to orders table in db'''
        count_added_to_db = self.db_client.add_orders_to_db()
        logging.info(f'Total of {count_added_to_db} new orders have been added to database, after exports were completed')

    def export_orders(self, testing=False):
        '''Summing up tasks inside ParseOrders class. Customizable under testing=True w/ commenting out'''
        self._prepare_filepaths()
        self.sort_orders_by_shipment_company()
        if testing:
            print(f'TESTING: SUSPENDED ADDING TO DB, EXPORTING instead.')
            logging.info(f'Suspended export of orders due to flag testing value: {testing}')
            self.export_etonas()
            print('Closing db connection, The end.')
            self.db_client.close_connection()
            # self.push_orders_to_db()
            # print(f'Finished. File exports suspended, orders added to DB due to flag testing value: {testing}')
            return
        self.export_same_buyer_details()
        self.export_dpost()
        self.export_ups()
        self.export_etonas()
        self.push_orders_to_db()

if __name__ == "__main__":
    pass