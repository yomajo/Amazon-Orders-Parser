from parser_utils import get_total_price, order_contains_batteries, order_contains_cards_keywords
from parser_utils import uk_order_contains_dp_keywords, get_origin_country, shorten_word_sequence
from parser_utils import get_dpost_product_header_val, get_lp_priority, get_lp_registered, uk_order_contains_lp_keywords
from parser_utils import get_order_ship_price, get_order_country, validate_LP_siuntos_rusis_header
from file_utils import get_output_dir, delete_file
from parser_constants import EXPORT_CONSTANTS, EU_COUNTRY_CODES, LP_COUNTRIES, TRACKED_COUNTRIES
from xlsx_exporter import EtonasExporter, NLPostExporter, DPDUPSExporter
from datetime import datetime
import logging
import csv
import sys
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

    Args:
    -orders - list of order dicts
    -db_client - object
    -proxy_keys = dict. Maps internal order keys (based on amazon) to external order headers(keys)
    -sales_channel - str ('AmazonEU'/'AmazonCOM'/'Etsy')
    
    export_orders(testing=False) : main method, sorts orders by shipment company, if testing flag is False,
    exports files with appropriate orders data and adds all passed orders when creating class to database'''
    
    def __init__(self, all_orders:list, db_client:object, proxy_keys:dict, sales_channel:str):
        self.all_orders = all_orders
        self.db_client = db_client
        self.proxy_keys = proxy_keys
        self.sales_channel = sales_channel
        self.dpost_orders = []
        self.lp_orders = []
        self.lp_tracked_orders = []
        self.etonas_orders = []
        self.nlpost_orders = []
        self.dpdups_orders = []


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
                    f.write(f"\n\t\t{order[self.proxy_keys['same-buyer-order-id']]}\t\t{order[self.proxy_keys['ship-address-1']]} {order[self.proxy_keys['ship-address-2']]}")
        logging.info(f'Same Buyer Orders have been written to {self.same_buyers_filename} and being showed to client')
        os.startfile(self.same_buyers_filename)

    def get_same_buyer_orders(self):
        '''step1: collects {recipient-name: [{order1}, {order2}]} structure; step2: removes single orders'''
        recipient_name_keys_orders = {}
        for order in self.all_orders:
            # If name is in same_buyers_orders keys, append order dict as list item, else, add order dict as list
            if order[self.proxy_keys['recipient-name']] in recipient_name_keys_orders:
                recipient_name_keys_orders[order[self.proxy_keys['recipient-name']]].append(order)
            else:
                recipient_name_keys_orders[order[self.proxy_keys['recipient-name']]] = [order]
        # Filter for same person orders dict, where key is recipient name and value is a list of order dicts:
        for name_key in list(recipient_name_keys_orders):
            if len(recipient_name_keys_orders[name_key]) == 1:
                recipient_name_keys_orders.pop(name_key, None)
        return recipient_name_keys_orders

    def export_csv(self, csv_filename : str, headers : list, contents : list, delimiter:str=';'):
        '''exports data to csv details provided as func. args, don't export empty files'''
        if not contents:
            logging.info(f'Skipping {os.path.basename(csv_filename)} export. No new orders.')
            return
        try:
            with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as csv_f:
                writer = csv.DictWriter(csv_f, fieldnames=headers, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(contents)
            logging.info(f'CSV {csv_filename} created. Orders inside: {len(contents)}')
        except Exception as e:
            logging.error(f'Error occured while exporting data to csv. Error: {e}.Arguments:\nheaders: {headers}\ncontents: {contents[0].keys()}')


    def get_csv_export_ready_data(self, orders : list, headers_option : str) -> list:
        '''reduces orders to that needed in output csv, based on passed option from EXPORT_CONSTANTS'''
        assert headers_option in ['dp', 'lp'], 'Unexpected headers export option passed to get_csv_export_ready_data function. Expected dp or lp'
        try:
            export_ready_data = []
            headers_settings = EXPORT_CONSTANTS[headers_option]
            for order in orders:
                reduced_order = self.get_export_ready_order(order, headers_settings)
                if headers_option == 'dp':
                    validated_order = self.__validate_dpost_order(reduced_order)
                    export_ready_data.append(validated_order)
                else:    
                    # Most of LP valiation is made on VBA side, deleting some fields conditionally.
                    validated_order = self.__validate_lp_order(reduced_order)
                    export_ready_data.append(validated_order)
            return export_ready_data
        except Exception as e:
            print(VBA_ERROR_ALERT)
            logging.critical(f'Error while iterating collected row dicts and trying to reduce. Error: {e}')
            logging.critical(f'Order causing trouble: {order}')
            sys.exit()

    def get_export_ready_order(self, order : dict, headers_settings : dict) -> dict:
        '''outputs a dict, those keys correspong to target export csv headers based on passed headers_settings'''        
        export = {}
        title_proxy_key = self.proxy_keys.get('title', '')

        for header in headers_settings['headers']:
            # Fixed values and header mapping: 
            if header in headers_settings['fixed'].keys():
                export[header] = headers_settings['fixed'][header]

            elif header in headers_settings['mapping'].keys():
                # etsy data has no phone / email / ship-address-3. Preventing key error via dict.get()
                target_key = self.proxy_keys.get(headers_settings['mapping'][header], '')
                export[header] = order.get(target_key, '')

            # DP specific headers
            elif header == 'DECLARED_ORIGIN_COUNTRY_1':
                # etsy - no item title, hardcoding for etsy until weight mapping
                if title_proxy_key == '':
                    export[header] = 'CN'
                else:
                    export[header] = get_origin_country(order[self.proxy_keys['title']])
            elif header == 'PRODUCT':
                export[header] = get_dpost_product_header_val(order)
            elif header == 'CUST_REF':
                export[header] = order[self.proxy_keys['recipient-name']][:20]

            # LP specific headers
            elif header == 'Siuntos rūšis':
                export[header] = validate_LP_siuntos_rusis_header(order['vmdoption'], order['tracked'])
            elif header == 'Registruota':
                export[header] = get_lp_registered(order)
            elif header == 'Pirmenybinė/nepirmenybinė':
                export[header] = get_lp_priority(order)
            elif header == 'Delivery Method':
                service_level_proxy_key = self.proxy_keys.get('ship-service-level', '')
                optional_str = ' EXPEDITED' if order.get(service_level_proxy_key, '') == 'Expedited' else ''
                export[header] = order.get(service_level_proxy_key, '') + optional_str
            elif header == 'Vertė, eur':
                export[header] = order['total-eur']

            # Common headers
            elif header in ['DETAILED_CONTENT_DESCRIPTIONS_1', 'Siunčiamų daiktų pavadinimas']:
                export[header] = order['category']
            elif header in ['DECLARED_VALUE_1', 'TOTAL_VALUE', 'Vertė, eur']:
                export[header] = get_total_price(order, self.sales_channel)
            else:
                export[header] = ''
        return export


    def __validate_dpost_order(self, order : dict) -> dict:
        '''rearranges /shortens data fields on demand (charlimit for fields)
        Takes care of: address1,2,3 , name, postcode fields'''
        name = order['NAME']
        order['POSTAL_CODE'] = order['POSTAL_CODE'].upper()

        if len(name) > DPOST_NAME_CHARLIMIT:
            logging.debug('Order enters name shortening functions')
            order['NAME'] = shorten_word_sequence(name)

        if len(order['ADDRESS_LINE_1']) > DPOST_ADDRESS_CHARLIMIT or \
            len(order['ADDRESS_LINE_2']) > DPOST_ADDRESS_CHARLIMIT or \
            len(order['ADDRESS_LINE_3']) > DPOST_ADDRESS_CHARLIMIT:
            logging.debug('Order enters address reorganisation')
            order = self.__reorg_dpost_order_addr(order)        
        return order

    @staticmethod
    def __reorg_dpost_order_addr(order : dict) -> dict:
        '''reoganizes address fields, returns original order dict, if reorganization still exceeds fields' limits'''
        original_order = order.copy()
        logging.debug(f'Before address reorg:\nf1: {order["ADDRESS_LINE_1"]}\nf2: {order["ADDRESS_LINE_2"]}\nf3:{order["ADDRESS_LINE_3"]}')
        total_address_seq = order['ADDRESS_LINE_1'] + ' ' + order['ADDRESS_LINE_2'] + ' ' + order['ADDRESS_LINE_3']
        address_seq = total_address_seq.split()
        # Reset fields, declare availability flags
        order['ADDRESS_LINE_1'] = order['ADDRESS_LINE_2'] = order['ADDRESS_LINE_3'] = ''
        f1_not_filled = f2_not_filled = True
        # Reorganizing fields
        for addr_item in address_seq:
            if len(order['ADDRESS_LINE_1']) + len(addr_item) < DPOST_ADDRESS_CHARLIMIT and f1_not_filled:
                order['ADDRESS_LINE_1'] = order['ADDRESS_LINE_1'] + addr_item + ' '
            elif len(order['ADDRESS_LINE_2']) + len(addr_item) < DPOST_ADDRESS_CHARLIMIT and f2_not_filled:
                order['ADDRESS_LINE_2'] = order['ADDRESS_LINE_2'] + addr_item + ' '
                f1_not_filled = False
            elif len(order['ADDRESS_LINE_3']) + len(addr_item) < DPOST_ADDRESS_CHARLIMIT:
                order['ADDRESS_LINE_3'] = order['ADDRESS_LINE_3'] + addr_item + ' '
                f2_not_filled = False
            else:
                logging.warning(f'Address reorganization failed. Total address char count: {len(order["ADDRESS_LINE_1"])+len(order["ADDRESS_LINE_2"])+len(order["ADDRESS_LINE_3"])} could not fit into 3x{DPOST_ADDRESS_CHARLIMIT}')
                logging.warning(f'Warning VBA, returning original order: {original_order}')
                print(VBA_DPOST_CHARLIMIT_ALERT)
                return original_order
        logging.debug(f'After reorg:\nf1: {order["ADDRESS_LINE_1"]}\nf2: {order["ADDRESS_LINE_2"]}\nf3:{order["ADDRESS_LINE_3"]}')
        return order

    def __validate_lp_order(self, order : dict) -> dict:
        '''conditionally deletes some of the fields before export'''
        if order['Gavėjo šalies kodas'].upper() in EU_COUNTRY_CODES:
            order['Muitinės deklaracija turinys'] = ''
            order['Siunčiamų daiktų pavadinimas'] = ''
            order['Kiekis, vnt'] = ''
            order['Vertė, eur'] = ''
        return order

    def sort_orders_by_sales_channel(self, skip_etonas:bool):
        '''choose different routing functions based on orders source (COM/EU Amazon). Performs check in the end for empty lists'''
        logging.info(f'Sorting orders by shippment company specific to {self.sales_channel} ruleset')
        for order in self.all_orders:
            if order['shipping_service'] == 'nl':
                self.nlpost_orders.append(order)
            elif order['shipping_service'] == 'lp' and order['tracked']:
                self.lp_tracked_orders.append(order)
            elif order['shipping_service'] == 'lp' and order['tracked'] == False:
                self.lp_orders.append(order)
            elif order['shipping_service'] == 'dp':
                self.dpost_orders.append(order)
            elif order['shipping_service'] == 'etonas' and not skip_etonas:
                self.etonas_orders.append(order)
            elif order['shipping_service'] == 'ups' or order['shipping_service'] == 'dpd':
                self.dpdups_orders.append(order)
            else:
                # cheapest service was not selected, defaulting to older sorting based on sales channel and order specifics
                if self.sales_channel == 'AmazonEU':
                    self.sort_EU_order_by_shipment_company(order, skip_etonas)
                elif self.sales_channel == 'AmazonCOM':
                    self.sort_COM_order_by_shipment_company(order)
                elif self.sales_channel == 'Etsy':
                    self.sort_etsy_order_by_shipment_company(order)
        self.exit_no_new_orders()
    
    def sort_EU_order_by_shipment_company(self, order:dict, skip_etonas:bool):
        '''sorts individual order from AMAZON EU by shipment company'''
        if order[self.proxy_keys['ship-service-level']] == 'Expedited':
            self.dpdups_orders.append(order)
        elif get_order_country(order, self.proxy_keys) in TRACKED_COUNTRIES:
            if order_contains_batteries(order):
                self.lp_tracked_orders.append(order)
            else:
                self.dpost_orders.append(order)
        elif order_contains_batteries(order) or order_contains_cards_keywords(order) or get_order_country(order, self.proxy_keys) in LP_COUNTRIES:
            self.lp_orders.append(order)
        elif get_order_country(order, self.proxy_keys) in ['GB', 'UK']:
            # Route Etonas shipments with DPost if flag is on.
            if skip_etonas:
                self.dpost_orders.append(order)
            else:
                if uk_order_contains_dp_keywords(order):
                    self.dpost_orders.append(order)
                elif uk_order_contains_lp_keywords(order):
                    self.lp_orders.append(order)
                else:                    
                    self.etonas_orders.append(order)
        
        elif get_order_ship_price(order, self.proxy_keys) >= 10:
            self.dpdups_orders.append(order)
        else:
            self.dpost_orders.append(order)

    def sort_COM_order_by_shipment_company(self, order:dict):
        '''sorts individual order from AMAZON COM by shipment company'''
        if order[self.proxy_keys['ship-service-level']] == 'Expedited' or get_order_ship_price(order, self.proxy_keys) >= 10:
            self.dpdups_orders.append(order)
        else:
            self.lp_tracked_orders.append(order)

    def sort_etsy_order_by_shipment_company(self, order:dict):
        '''sorts individual order from Etsy by shipment company'''
        if order['shipping-eur'] >= 21:
            self.dpdups_orders.append(order)
        elif order['shipping-eur'] > 0 or order['tracked']:
            self.lp_tracked_orders.append(order)
        else:
            self.lp_orders.append(order)
    
    def exit_no_new_orders(self):
        '''terminates python program, closes db connection, warns VBA'''
        if not self.etonas_orders and not self.dpost_orders and not self.nlpost_orders and not self.lp_orders \
                and not self.dpdups_orders and not self.lp_tracked_orders:
            logging.info(f'No new orders for processing. Terminating, alerting VBA.')
            self.db_client.session.close()
            print(VBA_NO_NEW_JOB)
            sys.exit()
    
    def _prepare_filepaths(self):
        '''creates cls variables of files abs paths to be created one dir above this script dir'''
        output_dir = get_output_dir()
        lp_output_dir = get_output_dir(client_file=False)
        date_stamp = datetime.today().strftime("%Y.%m.%d %H.%M")
        self.same_buyers_filename = os.path.join(output_dir, f'{self.sales_channel}-Same Buyer {date_stamp}.txt')
        self.etonas_filename = os.path.join(output_dir, f'{self.sales_channel}-Etonas {date_stamp}.xlsx')
        self.nlpost_filename = os.path.join(output_dir, f'{self.sales_channel}-NLPost {date_stamp}.xlsx')
        self.dpost_filename = os.path.join(output_dir, f'{self.sales_channel}-DPost {date_stamp}.csv')
        self.dpdups_filename = os.path.join(output_dir, f'{self.sales_channel}-DPDUPS {date_stamp}.xlsx')        
        self.lp_filename = os.path.join(lp_output_dir, f'{self.sales_channel}-LP.csv')
        self.lp_tracked_filename = os.path.join(lp_output_dir, f'{self.sales_channel}-LP-Tracked.csv')

    def delete_old_files(self):
        '''addresses potential double loading of same LP sheets to Excel problem,
        deletes csv files from Helper Files dir before new run'''
        delete_file(self.lp_filename)
        delete_file(self.lp_tracked_filename)
    
    def export_dpost(self):
        '''export csv file for Deutsche Post shipping service'''
        if self.dpost_orders:
            dpost_content = self.get_csv_export_ready_data(self.dpost_orders, 'dp')
            self.export_csv(self.dpost_filename, EXPORT_CONSTANTS['dp']['headers'], dpost_content)

    def export_dpdups(self):
        '''export csv file for DPD/UPS shipping services'''
        if self.dpdups_orders:
            DPDUPSExporter(self.dpdups_orders, self.dpdups_filename, self.sales_channel, self.proxy_keys).export()
            logging.info(f'XLSX {self.dpdups_filename} created. Orders inside: {len(self.dpdups_orders)}')

    def export_lp(self):
        '''export csv file for Lietuvos Pastas shipping service'''
        if self.lp_orders:
            lp_content = self.get_csv_export_ready_data(self.lp_orders, 'lp')
            self.export_csv(self.lp_filename, EXPORT_CONSTANTS['lp']['headers'], lp_content)

    def export_lp_tracked(self):
        '''export csv file for Lietuvos Pastas (TRACKED orders) shipping service'''
        if self.lp_tracked_orders:
            lp_content = self.get_csv_export_ready_data(self.lp_tracked_orders, 'lp')
            self.export_csv(self.lp_tracked_filename, EXPORT_CONSTANTS['lp']['headers'], lp_content)

    def export_etonas(self):
        '''export xlsx file for Etonas shipping service'''
        if self.etonas_orders:
            EtonasExporter(self.etonas_orders, self.etonas_filename, self.sales_channel, self.proxy_keys).export()
            logging.info(f'XLSX {self.etonas_filename} created. Orders inside: {len(self.etonas_orders)}')
    
    def export_nlpost(self):
        '''export xlsx file for NLPost shipping service'''
        if self.nlpost_orders:
            NLPostExporter(self.nlpost_orders, self.nlpost_filename, self.sales_channel, self.proxy_keys).export()
            logging.info(f'XLSX {self.nlpost_filename} created. Orders inside: {len(self.nlpost_orders)}')

    def push_orders_to_db(self):
        '''adds all orders in this class to orders table in db'''
        count_added_to_db = self.db_client.add_orders_to_db()
        logging.info(f'Total of {count_added_to_db} new orders have been added to database, after exports were completed')

    def test_exports(self, testing=False, skip_etonas=False):
        '''customize what shall happen when testing=True'''
        print(f'TESTING FLAG IS: {testing}. Refer to test_exports in parse_orders.py')
        logging.info(f'TESTING FLAG IS: {testing}. Refer to test_exports in parse_orders.py')
        # self.export_same_buyer_details()
        self.export_dpost()
        self.export_lp()
        self.export_lp_tracked()
        self.export_etonas()
        self.export_nlpost()
        self.export_dpdups()
        # self.push_orders_to_db()
        self.db_client.session.close()
        print(f'Finished executing ParseOrders.test_exports(testing={testing}) ')
    
    def export_orders(self, testing=False, skip_etonas=False):
        '''Summing up tasks inside ParseOrders class. When testing, behaviour customizable inside
        test_exports method'''
        self._prepare_filepaths()
        self.delete_old_files()
        self.sort_orders_by_sales_channel(skip_etonas)
        if testing:
            self.test_exports(testing, skip_etonas)
            return
        self.export_same_buyer_details()
        self.export_dpost()
        self.export_lp()
        self.export_lp_tracked()
        self.export_etonas()
        self.export_nlpost()
        self.export_dpdups()
        self.push_orders_to_db()
        self.db_client.session.close()


if __name__ == "__main__":
    pass