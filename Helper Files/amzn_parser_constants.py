# Includes strange code for Greece (EL)
EU_COUNTRY_CODES = [
    'BE',
    'BG',
    'CZ',
    'DK',
    'DE',
    'EE',
    'IE',
    'EL',
    'GR',
    'ES',
    'FR',
    'HR',
    'IT',
    'CY',
    'LV',
    'LT',
    'LU',
    'HU',
    'MT',
    'NL',
    'AT',
    'PL',
    'PT',
    'RO',
    'SI',
    'SK',
    'FI',
    'SE'
]

ORIGIN_COUNTRY_CRITERIAS = [
    ['copag', '', 'BR'],
    ['ellusionist', '', 'BE'],
    ['cartamundi', '', 'BE'],
    ['fournier', '', 'ES'],
    ['bicycle', '', 'US'],
    ['aviator',	'', 'US'],
    ['bee', 'deck', 'US'],
    ['theory','', 'US'],
    ['lo scarabeo', '', 'IT'],
    ['agm', 'cards', 'BE'],
    ['agm', 'karten', 'BE'],
    ['bomb cosm', '', 'UK']
    ]

CATEGORY_CRITERIAS = [
    ['energizer', '', 'ENERGIZER', 'BATTERIES'],
    ['duracell', '', 'DURACELL', 'BATTERIES'],
    ['varta', '', 'VARTA', 'BATTERIES'],
    ['rayovac', '', 'RAYOVAC', 'BATTERIES'],
    ['renata', '', 'RENATA', 'BATTERIES'],
    ['maxell', '', 'MAXELL', 'BATTERIES'],
    ['murata', '', 'SONY MURATA', 'BATTERIES'],
    ['sony', '', 'SONY', 'BATTERIES'],
    ['vinnic', '', 'VINNIC', 'BATTERIES'],
    ['siemens', '', 'SIEMENS', 'BATTERIES'],
    ['gp', 'batt', 'GP'	'BATTERIES'],
    ['everactive', '', 'EVERACTIVE', 'BATTERIES'],
    ['eneloop', '', 'P ENELOOP', 'BATTERIES'],
    ['panasonic', '', 'PANASONIC', 'BATTERIES'],
    ['procell', '', 'PROCELL', 'BATTERIES'],
    ['xtar', 'batt', 'XTAR', 'BATTERIES'],
    ['samsung', '', 'LI-ION', 'BATTERIES'],
    ['sanyo', '', 'LI-ION', 'BATTERIES'],
    ['eve', '', 'LI-ION', 'BATTERIES'],
    ['kodak', '', 'KODAK', 'BATTERIES'],
    ['saft', '', 'LI-ION', 'BATTERIES'],
    ['li-ion', '', 'LI-ION', 'BATTERIES'],
    ['batt', '', 'ZBATTERY BRAND', 'BATTERIES'],
    ['copag', '', 'COPAG', 'PLAYING CARDS'],
    ['ellusionist', '', 'ELLUSIONIST', 'PLAYING CARDS'],
    ['cartamundi', '', 'CARTAMUNDI', 'PLAYING CARDS'],
    ['fournier', '', 'BICYCLE', 'PLAYING CARDS'],
    ['bicycle', '', 'BICYCLE', 'PLAYING CARDS'],
    ['aviator', '', 'BICYCLE', 'PLAYING CARDS'],
    ['bee', 'deck', 'BICYCLE', 'PLAYING CARDS'],
    ['theory', '', 'THEORY11', 'PLAYING CARDS'],
    ['maverick', '', 'BICYCLE', 'PLAYING CARDS'],
    ['streamline', '', 'BICYCLE', 'PLAYING CARDS'],
    ['hoyle', '', 'BICYCLE', 'PLAYING CARDS'],
    ['tally', '', 'BICYCLE', 'PLAYING CARDS'],
    ['cartes', '', 'OTHER CARDS BRAND', 'PLAYING CARDS'], # Additional for amazon
    ['llewellyn', '', 'LLEWELLYN', 'TAROT CARDS'],
    ['lo scarabeo', '', 'LO SCARABEO', 'TAROT CARDS'],
    ['agm', 'cards', 'AGM', 'TAROT CARDS'],
    ['agm', 'karten', 'AGM', 'TAROT CARDS'],
    ['us games', '', 'US GAMES', 'TAROT CARDS'],
    ['blue angel', '', 'BLUE ANGELS', 'TAROT CARDS'],
    ['schiffer', '', 'SCHIFFER', 'TAROT CARDS'],
    ['FOOTBALL', '', 'FOOTBOOL', 'FOOTBALL'],
    ['fußball', '', 'FOOTBOOL', 'FOOTBALL'],
    ['nfl', '', 'FOOTBOOL', 'FOOTBALL'],
    ['nba', '', 'FOOTBOOL', 'FOOTBALL'],
    ['basketball', '', 'FOOTBOOL', 'FOOTBALL'],
    ['bomb cosm', '', 'BOMB COSM', 'OTHERS'],
    ['baff', '', 'GELLI BAFF', 'OTHERS'],
    ['injinji', '', 'INJINJI', 'OTHERS']
    ]

# New Etonas Headers:
ETONAS_HEADERS = [
    'Address_line_1',
    'Address_line_2',
    'Address_line_3',
    'Address_line_4',
    'Postcode',
    'First_name',
    'Last_name',
    'Email',
    'Weight(Kg)',
    'Compensation()',
    'Signature(y/n)',
    'Reference',
    'Contents',
    'Delivery_phone',
    'Buyer Country',
    'Tracking (0 - neregistruota, 1 - registruota)',
    'PackageType',
    'Amount',
    'Sum'
    ]

DPOST_HEADERS = [
    'PRODUCT',
    'SERVICE_LEVEL', 
    'CUST_EKP', 
    'AWB', 
    'REGISTERED_BARCODE', 
    'CUST_REF', 
    'NAME', 
    'RECIPIENT_PHONE', 
    'RECIPIENT_EMAIL', 
    'ADDRESS_LINE_1', 
    'ADDRESS_LINE_2', 
    'ADDRESS_LINE_3', 
    'CITY', 
    'STATE', 
    'POSTAL_CODE', 
    'DESTINATION_COUNTRY', 
    'WEIGHT', 
    'CURRENCY', 
    'CONTENT_TYPE', 
    'DECLARED_CONTENT_AMOUNT_1', 
    'DETAILED_CONTENT_DESCRIPTIONS_1', 
    'DECLARED_NETWEIGHT_1', 
    'DECLARED_VALUE_1', 
    'DECLARED_HS_CODE_1', 
    'DECLARED_ORIGIN_COUNTRY_1', 
    'DECLARED_CONTENT_AMOUNT_2', 
    'DETAILED_CONTENT_DESCRIPTIONS_2', 
    'DECLARED_NETWEIGHT_2', 
    'DECLARED_VALUE_2', 
    'DECLARED_HS_CODE_2', 
    'DECLARED_ORIGIN_COUNTRY_2', 
    'DECLARED_CONTENT_AMOUNT_3', 
    'DETAILED_CONTENT_DESCRIPTIONS_3', 
    'DECLARED_NETWEIGHT_3', 
    'DECLARED_VALUE_3', 
    'DECLARED_HS_CODE_3', 
    'DECLARED_ORIGIN_COUNTRY_3', 
    'DECLARED_CONTENT_AMOUNT_4', 
    'DETAILED_CONTENT_DESCRIPTIONS_4', 
    'DECLARED_NETWEIGHT_4', 
    'DECLARED_VALUE_4', 
    'DECLARED_HS_CODE_4', 
    'DECLARED_ORIGIN_COUNTRY_4', 
    'DECLARED_CONTENT_AMOUNT_5', 
    'DETAILED_CONTENT_DESCRIPTIONS_5', 
    'DECLARED_NETWEIGHT_5', 
    'DECLARED_VALUE_5', 
    'DECLARED_HS_CODE_5', 
    'DECLARED_ORIGIN_COUNTRY_5', 
    'TOTAL_VALUE',
    'RETURN_LABEL',
    'SENDER_CUSTOMS_REFERENCE',
    'IMPORTER_CUSTOMS_REFERENCE'
    ]

# Mapping: key corresponds to DPost CSV template (only the ones used for data entry), value - corresponding amazon header title
DPOST_HEADERS_MAPPING = {
    'NAME' : 'recipient-name',
    'CUST_REF' : 'recipient-name',
    'RECIPIENT_PHONE' : 'buyer-phone-number',
    'RECIPIENT_EMAIL' : 'buyer-email',
    'ADDRESS_LINE_1' : 'ship-address-1',
    'ADDRESS_LINE_2' : 'ship-address-2',
    'ADDRESS_LINE_3' : 'ship-address-3',
    'CITY' : 'ship-city',
    'STATE': 'ship-state',
    'POSTAL_CODE' : 'ship-postal-code',
    'DESTINATION_COUNTRY' : 'ship-country',
    'DECLARED_CONTENT_AMOUNT_1' : 'quantity-purchased',
    'CURRENCY' : 'currency'
    }

DPOST_FIXED_VALUES = {
    'PRODUCT' : 'GMP',
    'SERVICE_LEVEL' : 'PRIORITY',
    'CONTENT_TYPE' : 'SALE_GOODS',
    'WEIGHT' : '100',
    'DECLARED_NETWEIGHT_1' : '100',
    'RETURN_LABEL' :'FALSE'
    }

ETONAS_HEADERS_MAPPING = {
    'Address_line_1' : 'ship-address-1',
    'Address_line_2' : 'ship-address-2',
    'Address_line_3' : 'ship-city',
    'Address_line_4' : 'ship-state',
    'Postcode' : 'ship-postal-code',
    'Email' : 'buyer-email',
    'Delivery_phone' : 'buyer-phone-number',
    'Buyer Country': 'ship-country'
    }

LP_HEADERS = [
    'Delivery Method',
    'Terminalo ID',
    'Siuntos rūšis',
    'Gavėjo pavadinimas',
    'Gavėjo gatvė',
    'Gavėjo namas',
    'Gavėjo butas',
    'Gavėjo gyvenvietė',
    'Gavėjo pašto kodas',
    'Gavėjo šalies kodas',
    'Gavėjo mob. tel. (370xxxxxxxx)',
    'Gavėjo el. paštas',
    'Svoris (g)',
    'Dalių skaičius',
    'Registruota',
    'Pirmenybinė/nepirmenybinė',
    'Įvertinimas (Eur)',
    'Išperkamasis mokestis (Eur)',
    'Įteikti asmeniškai',
    'Su įteikimo pranešimu',
    'Gavėjo p.d. numeris',
    'Iki pareikalavimo',
    'Moka gavėjas',
    'Komentaras',
    'Muitinės deklaracija turinys',
    'Siunčiamų daiktų pavadinimas',
    'Kiekis, vnt',
    'Svoris, g',
    'Vertė, eur',
    'Nevykus pristatymui , grąžinti siuntą po ( nurodyti dienų skaičių)'
    ]

LP_HEADERS_MAPPING = {
    'Delivery Method' : 'currency',
    'Gavėjo pavadinimas' : 'recipient-name',
    'Gavėjo mob. tel. (370xxxxxxxx)' : 'buyer-phone-number',
    'Gavėjo el. paštas' : 'buyer-email',
    'Gavėjo gatvė' : 'ship-address-1',
    'Gavėjo namas' : 'ship-address-2',
    'Gavėjo butas' : 'ship-address-3',
    'Gavėjo gyvenvietė' : 'ship-city',
    'Gavėjo pašto kodas' : 'ship-postal-code',
    'Gavėjo šalies kodas' : 'ship-country',
    'Kiekis, vnt' : 'quantity-purchased',
    'Vertė, eur' : 'item-price'
    }

LP_FIXED_VALUES = {
    'Muitinės deklaracija turinys' : 'Dovana'
    }

BATTERY_BRANDS = [
    'RENATA',
    'VINNIC',
    'EVERACTIVE',
    'MAXELL',
    'RAYOVAC',
    'KODAK',
    'XTAR',
    'PANASONIC',
    'SONY',
    'VARTA',
    'ENERGIZER',
    'DURACELL',
    'SAFT',
    'SIEMENS',
    'SIGNIA',
    'SAMSUNG',
    'SANYO',
    'LG',
    'GP',
    'TADIRAN',
    'BATTERIES'
    ]

EXPORT_CONSTANTS = {
                'dp' : {'headers' : DPOST_HEADERS, 'mapping' : DPOST_HEADERS_MAPPING, 'fixed' : DPOST_FIXED_VALUES},
                'lp' : {'headers' : LP_HEADERS, 'mapping' : LP_HEADERS_MAPPING, 'fixed' : LP_FIXED_VALUES}
                }

LP_COUNTRIES = [
    'IE',
    'SE',
    'LT',
    'FI',
    'EE',
    'LV',
    'NO',
    'CH',
    'IS'
]