from parser_utils import dump_to_json
from bs4 import BeautifulSoup
import requests
import logging
import lxml

ECB_XML_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
TARGET_CURRENCIES = ['USD', 'CAD', 'AUD', 'HKD', 'SGD']

# GLOBAL VARIABLES
VBA_FOREX_ALERT = 'FOREX FAILURE'


def get_request():
    try:
        r = requests.get(ECB_XML_URL, timeout=10)
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

def get_soup(response) -> object:
    return BeautifulSoup(response.text, 'lxml')

def rates_from_soup(soup:object) -> dict:
    '''parses xml soup, returns rates as dict as:

    {'last_updated':new_update_date,
        currencies: {
            USD: rate1,
            CAD:rate2,
            ...}}'''
    xml_data = {}
    try:
        update_date = soup.cube.cube['time']
        xml_data['last_updated'] = update_date
        xml_data['currencies'] = {}

        cubes = soup.findAll('cube', {'currency':TARGET_CURRENCIES})
        for cube in cubes:

            currency = cube['currency']
            rate = cube['rate']
            xml_data['currencies'][currency] = rate        
        return xml_data
    except Exception as e:
        logging.warning(f'Failed to parse soup object. Likely changes in ECB XML structure. Returning None instead of dict.')
        return None


def run():
    # check if update is neccessary (days diff since last update > 1 ). 
    # get request

    r = get_request()
    if not r:
        # alert VBA, use existing FX rates (get last updated from file)
        logging.warning(f'Failed to get response, alerting VBA about use of older FX rates r.status_code: {r.status_code}')
        print(VBA_FOREX_ALERT)
        return

    # create/update
    soup = get_soup(r)

    # update/create json
    rates_obj = rates_from_soup(soup)
    
    dump_to_json(rates_obj, 'rates.json')

    print('check json, babe')




if __name__ == '__main__':
    run()