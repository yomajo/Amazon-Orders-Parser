from file_utils import get_output_dir, dump_to_json, read_json_to_obj
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import logging
import lxml
import sys
import os


# GLOBAL VARIABLES
ECB_XML_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
SUPPORTED_CURRENCIES = ['USD', 'GBP', 'CAD', 'CDN', 'AUD', 'HKD', 'SGD', 'SEK', 'PLN', 'MXN']
RATES_JSON = 'fx.json'
VBA_NO_FX_RATES = 'NO FOREX DATA IN PYTHON SIDE'
VBA_FOREX_ALERT = 'FOREX FAILURE'


class Forex():
    '''all things related to currency conversion. FX data source: ECB xml
    access supported pairs dictionary {'currency': float, ...} through instance variable 'rates'
    
    main method for external use:

    convert_to_eur(amount:float, currency:str)'''

    def __init__(self):
        self.json_path = os.path.join(get_output_dir(client_file=False), RATES_JSON)
        self.rates_file = self.__get_rates_file()
        if self.__requires_update():
            self.rates_file = self.__download_fresh_rates()
        self.rates = self._get_rates()

    def __get_rates_file(self):
        '''returns fx data json file path'''
        if os.path.exists(self.json_path):
            self.prior_file = True
            return self.json_path
        else:
            self.prior_file = False
            logging.debug(f'No prior FX json file. Initializing...')
            return self.__download_fresh_rates()

    def __download_fresh_rates(self):
        '''downloads fresh rates, writes to json, returs path of newly saved json file'''
        logging.info(f'Updating FX rates json...')
        rates = self.__get_new_rates_obj()
        # handling case if older file exists, but new fails to download and __get_new_rates_obj returns {}
        if rates:
            logging.info(f'FX rates have been updated. Last update date: {rates["last_updated"]}')
            return dump_to_json(rates, RATES_JSON)
        else:
            return self.json_path

    def __get_new_rates_obj(self) -> dict:
        '''returns new rates dictionary'''
        try:
            r = self.__get_request()
            soup = self.__get_soup(r)
            return self.__get_rates_from_soup(soup)
        except Exception as e:
            if self.prior_file:
                logging.warning(f'Failed inside __get_new_rates. Alerting VBA about use of older FX rates. Err: {e}')
                print(VBA_FOREX_ALERT)
                return {}
            else:
                print(VBA_NO_FX_RATES)
                logging.critical(f'Failed to initialize fx json file on initial run. Terminating immediately, VBA warned. Err: {e}')
                sys.exit()

    def __get_request(self):
        try:
            r = requests.get(ECB_XML_URL, timeout=4)
            if r.ok:
                return r
            else:
                raise Exception(f'Something wrong with ECB XML. Response: {r}')
        except TimeoutError as e:
            logging.warning(f'Could not get ECB response for: {ECB_XML_URL} within 10 secods. Err: {e}. Returning None')
            return None
        except Exception as e:
            logging.warning(f'Could not get response for: {ECB_XML_URL} Err: {e}. Returning None')
            return None

    def __get_soup(self, response:object) -> object:
        '''returns BeautifulSoup object for parsing'''
        return BeautifulSoup(response.text, 'lxml')

    def __get_rates_from_soup(self, soup:object) -> dict:
        '''parses xml soup, returns rates as dict as:

        {'last_updated' : new_update_date,
        'currencies' : {
                USD: rate1,
                CAD:rate2,
                ...}}'''
        xml_data = {}
        try:
            update_date = soup.cube.cube['time']
            xml_data['last_updated'] = update_date
            xml_data['currencies'] = {}

            cubes = soup.findAll('cube', {'currency':SUPPORTED_CURRENCIES})
            for cube in cubes:
                currency = cube['currency']
                rate = cube['rate']
                xml_data['currencies'][currency] = float(rate)        
            return xml_data
        except Exception as e:
            logging.warning(f'Failed to parse soup object. Likely changes in ECB XML structure. Returning None instead of dict. Err: {e}')
            return None
    
    def __requires_update(self):
        '''compares date in self.rates_file to today's date. If older than 2 days, returns True'''
        try:
            json_data = read_json_to_obj(self.rates_file)
            last_updated_raw = json_data['last_updated']
            last_updated = datetime.strptime(last_updated_raw, '%Y-%m-%d')
            today = datetime.today()
            if (today - last_updated).days >= 2:
                return True
            else:
                return False
        except Exception as e:
            print(VBA_FOREX_ALERT)
            logging.warning(f'Failed to compare dates. ECB changed data format? Returning True. VBA Alerted. Err: {e}')
            return True

    def _get_rates(self):
        '''returns rates dict'''
        rates = read_json_to_obj(self.rates_file)
        return rates['currencies']
    
    def get_fx_rate(self, target_currency):
        '''returns fx rate for target currency'''
        if target_currency in SUPPORTED_CURRENCIES:
            return self.rates[target_currency]
        else:
            return None
    
    def convert_to_eur(self, amount:float, currency:str):
        '''converts amount of currency to EUR, works w/ currencies in SUPPORTED_CURRENCIES
        NOTE: silently returns original amount for Amazon replacement orders (empty currency)'''
        currency = currency.upper()
        if currency == 'EUR' or currency == '':
            return amount
        elif currency in SUPPORTED_CURRENCIES:
            currency_adj = 'CAD' if currency == 'CDN' else currency
            return round(amount / self.rates[currency_adj], 2)
        else:
            logging.warning(f'Attempted currency conversion w/ unsupported currency: {currency}. Alerting VBA, returning original amount')
            print(VBA_FOREX_ALERT)
            return amount


if __name__ == '__main__':
    pass