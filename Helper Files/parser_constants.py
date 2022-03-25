
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
    ['llewellyn', '', 'LLEWELLYN', 'TAROT CARDS'],
    ['lo scarabeo', '', 'LO SCARABEO', 'TAROT CARDS'],
    ['agm', 'cards', 'AGM', 'TAROT CARDS'],
    ['agm', 'karten', 'AGM', 'TAROT CARDS'],
    ['solarus',	'', 'SOLARUS', 'TAROT CARDS'],
    ['animal dreaming', '',	'ANIMAL DREAMING', 'TAROT CARDS'],
    ['findhorn', '', 'FINDHORN PRESS', 'TAROT CARDS'],
    ['cico', '', 'CICO BOOKS', 'TAROT CARDS'],
    ['bear', 'company', 'BEAR & COMPANY', 'TAROT CARDS'],
    ['tarcher', '', 'TARCHER', 'TAROT CARDS'],
    ['world tree', '', 'WORLD TREE PRESS', 'TAROT CARDS'],
    ['earth dancer', '', 'EARTH DANCER', 'TAROT CARDS'],
    ['inner traditions', '', 'INNER TRADITIONS', 'TAROT CARDS'],
    ['harper', '', 'HARPER ONE', 'TAROT CARDS'],
    ['touchstone', '', 'TOUCHSTONE', 'TAROT CARDS'],
    ['destiny', '', 'DESTINY', 'TAROT CARDS'],
    ['rockpool', '', 'ROCKPOOL', 'TAROT CARDS'],
    ['music design', '', 'MUSIC DESIGN', 'TAROT CARDS'],
    ['adams media', '', 'ADAMS MEDIA', 'TAROT CARDS'],
    ['welbeck',	'',	'WELLBECK', 'TAROT CARDS'],
    ['beyond words', '', 'BEYOND WORDS', 'TAROT CARDS'],
    ['us games', '', 'US GAMES', 'TAROT CARDS'],
    ['blue angel', '', 'BLUE ANGELS', 'TAROT CARDS'],
    ['schiffer', '', 'SCHIFFER', 'TAROT CARDS'],
    ['fournier', 'tarot', 'FOURNIER', 'TAROT CARDS'],
    ['copag', 'casino', 'COPAG', 'TAROT CARDS'],
    ['angel', 'card', 'OTHER CARDS BRAND', 'TAROT CARDS'],
    ['oracle', '', 'OTHER CARDS BRAND', 'TAROT CARDS'],
    ['tarot', '', 'OTHER CARDS BRAND', 'TAROT CARDS'], # Generic for Tarot cards

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
    ['art of play', '', 'ART OF PLAY', 'PLAYING CARDS'],
    ['cartes', '', 'OTHER CARDS BRAND', 'PLAYING CARDS'], # Additional for amazon
    ['cards', '', 'OTHER CARDS BRAND', 'PLAYING CARDS'], # another generic for playing cards
    
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
    ['gp', 'batt', 'GP', 'BATTERIES'],
    ['gp', 'recyko', 'GP', 'BATTERIES'],
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
    ['camelion', '', 'CAMELION', 'BATTERIES'],
    ['philips', '', 'PHILIPS', 'BATTERIES'],
    ['pila', '', 'ZBATTERY BRAND', 'BATTERIES'],
    ['batt', '', 'ZBATTERY BRAND', 'BATTERIES'],

    ['FOOTBALL', '', 'FOOTBOOL', 'FOOTBALL'],
    ['fußball', '', 'FOOTBOOL', 'FOOTBALL'],
    ['nfl', '', 'FOOTBOOL', 'FOOTBALL'],
    ['nba', '', 'FOOTBOOL', 'FOOTBALL'],
    ['basketball', '', 'FOOTBOOL', 'FOOTBALL'],
    ['bomb cosm', '', 'BOMB COSM', 'OTHERS'],
    ['baff', '', 'GELLI BAFF', 'OTHERS'],
    ['injinji', '', 'INJINJI', 'OTHERS'],
    ['q-workshop', '', 'Q-WORKSHOP', 'DICE']
    ]

NLPOST_HEADERS = [
    'Sender company',
    'Sender name',
    'Sender street',
    'Sender city',
    'Sender postal code',
    'Sender country code',
    'Sender state code',
    'Sender phone',
    'Sender email',
    'Sender EORI',
    'Sender VAT',
    'Receiver company name',
    'Receiver name',
    'Receiver street',
    'Receiver city',
    'Receiver postal code',
    'Receiver country code',
    'Receiver state',
    'Receiver phone',
    'Receiver email',
    'Receiver EORI',
    'Receiver VAT',
    'Type',
    'Parcels amount',
    'X',
    'Y',
    'Z',
    'Weight',
    'Units',
    'Description',
    'Unit price',
    'Service name',
    'Order reference',
    'Export reason',
    'Export country code',
    'HS code',
    'COD',
    'COD Currency',
    'Importer',
    'identifier',
]

NLPOST_FIXED_VALUES = {
    'Sender company' : 'Shop4Top',
    'Sender name' : 'Vykintas Urniezius',
    'Sender street' : 'Veiveriu street 55B',
    'Sender city' : 'Kaunas',
    'Sender postal code' : '46335',
    'Sender country code' : 'LT',
    'Sender phone' : '861066162',
    'Sender email' : 'klausimai@shop4top.lt',
    'Type' : 'Package',
    'Parcels amount' : '1',
    'Units' : '1',
    'Export reason' : 'Gift',
}

# corresponding to proxy keys for etsy / amazon
NLPOST_HEADERS_MAPPING = {
    'Receiver name' : 'recipient-name',
    'Receiver city' : 'ship-city',
    'Receiver postal code' : 'ship-postal-code',
    'Receiver country code' : 'ship-country',
    'Receiver state' : 'ship-state',
    'Receiver phone' : 'buyer-phone-number',
    'Receiver email' : 'buyer-email',
    'Description' : 'category',
    'Order reference' : 'order-id',
    'Export country code' : 'ship-country',
    'COD Currency' : 'currency',
}

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
    'PackageType (DP Jeigu maza pakuote)',
    'Amount',
    'Price per quantity',
    'GLS',
    'HS',
    'Origin',
    'Currency'
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

# Mapping: key corresponds to DPost CSV template (only the ones used for data entry)
# value - corresponding proxy_keys header title for amazon/etsy
DPOST_HEADERS_MAPPING = {
    'NAME' : 'recipient-name',
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
    'CURRENCY' : 'currency',
    'WEIGHT' : 'weight',
    'DECLARED_NETWEIGHT_1' : 'weight',
    'DETAILED_CONTENT_DESCRIPTIONS_1' : 'category',
    }

DPOST_FIXED_VALUES = {
    'SERVICE_LEVEL' : 'PRIORITY',
    'CONTENT_TYPE' : 'SALE_GOODS',
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
    'Buyer Country': 'ship-country',
    'Currency' : 'currency',
    'Amount' : 'quantity-purchased',
    'Contents' : 'category',
    }

LP_HEADERS = [
    'Delivery Method',
    'Siuntos rūšis',
    'Terminalo ID',
    'Gavėjo pavadinimas',
    'Gavėjo įmonės pavadinimas',
    'Gavėjo gatvė',
    'Gavėjo namas',
    'Gavėjo butas',
    'Gavėjo gyvenvietė',
    'Gavėjo pašto kodas',
    'Adreso eilutė 1',
    'Adreso eilutė 2',
    'Gavėjo šalies kodas',
    'Gavėjo mob. tel. (370xxxxxxxx)',
    'Gavėjo el. paštas',
    'Svoris (g)',
    'Dalių skaičius',
    'Pirmenybinis siuntimas',
    'Draudimas (Eur)',
    'COD (Eur)',
    'Gauti informaciją apie įteiktą siuntą (POD)',
    'Moka gavėjas',
    'Komentaras',
    'Siuntos turinio kategorija',
    'HS kodas',
    'Prekių kilmės šalis',
    'Siuntos turinio aprašymas anglų kalba',
    'Kiekis (vnt)',
    'Deklaruojamas siuntos svoris (g)',
    'Deklaruojama vertė (eur)',
    'Nepavykus pristatyti',
]

LP_HEADERS_MAPPING = {
    'Gavėjo pavadinimas' : 'recipient-name',
    'Gavėjo mob. tel. (370xxxxxxxx)' : 'buyer-phone-number',
    'Gavėjo el. paštas' : 'buyer-email',
    'Gavėjo pašto kodas' : 'ship-postal-code',
    'Gavėjo gyvenvietė' : 'ship-city',
    'Gavėjo šalies kodas' : 'ship-country',
    'Svoris (g)' : 'weight',
    'Kiekis (vnt)' : 'quantity-purchased',
    'Deklaruojamas siuntos svoris (g)' : 'weight',
    }

LP_FIXED_VALUES = {
    'Siuntos turinio kategorija' : 'Dovana'
    }


DPDUPS_HEADERS = [
    'Order ID',
    'Buyer Name',
    'Country',
    'Weight',
    'Service Picked',
    'Tracked',
    'Sales Channel',
]

DPDUPS_HEADERS_MAPPING = {
    'Order ID' : 'order-id',
    'Buyer Name' : 'recipient-name',
    'Country' : 'ship-country',
    'Weight' : 'weight',
}

EXPORT_CONSTANTS = {
                'dp' : {'headers' : DPOST_HEADERS, 'mapping' : DPOST_HEADERS_MAPPING, 'fixed' : DPOST_FIXED_VALUES},
                'lp' : {'headers' : LP_HEADERS, 'mapping' : LP_HEADERS_MAPPING, 'fixed' : LP_FIXED_VALUES}
                }

EXPECTED_SALES_CHANNELS = ['AmazonCOM', 'AmazonEU', 'Etsy']

AMAZON_KEYS = {
    'order-id' : 'order-item-id',
    'secondary-order-id' : 'order-id',
    'same-buyer-order-id' : 'order-id',
    'purchase-date' : 'purchase-date',
    'payments-date' : 'payments-date',
    'buyer-email' : 'buyer-email',
    'buyer-name' : 'buyer-name',
    'buyer-phone-number' : 'buyer-phone-number',
    'sku' : 'sku',
    'title' : 'product-name',
    'quantity-purchased' : 'quantity-purchased',
    'currency' : 'currency',
    'item-price' : 'item-price',
    'item-tax' : 'item-tax',
    'shipping-price' : 'shipping-price',
    'shipping-tax' : 'shipping-tax',
    'ship-service-level' : 'ship-service-level',
    'recipient-name' : 'recipient-name',
    'ship-address-1' : 'ship-address-1',
    'ship-address-2' : 'ship-address-2',
    'ship-address-3' : 'ship-address-3',
    'ship-city' : 'ship-city',
    'ship-state' : 'ship-state',
    'ship-postal-code' : 'ship-postal-code',
    'ship-country' : 'ship-country',
    'ship-phone-number' : 'ship-phone-number',
    'delivery-start-date' : 'delivery-start-date',
    'delivery-end-date' : 'delivery-end-date',
    'delivery-time-zone' : 'delivery-time-zone',
    'delivery-Instructions' : 'delivery-Instructions',
    'sales-channel' : 'sales-channel',
    # added during processing
    'weight' : 'weight',
    'category' : 'category',
    'brand' : 'brand',
    'vmdoption' : 'vmdoption',
}

ETSY_KEYS = {
    'order-id' : 'Order ID',
    'same-buyer-order-id' : 'Order ID',
    'purchase-date' : 'Sale Date',
    'recipient-name' : 'Full Name',
    'buyer-name' : 'Full Name',
    'buyer-fname' : 'First Name',
    'buyer-lname' : 'Last Name',
    'payments-date' : 'Date Shipped',
    'ship-address-1' : 'Street 1',
    'ship-address-2' : 'Street 2',
    'ship-city' : 'Ship City',
    'ship-state' : 'Ship State',
    'ship-postal-code' : 'Ship Zipcode',
    'ship-country' : 'Ship Country',
    'currency' : 'Currency',
    'quantity-purchased' : 'Number of Items',
    'sku' : 'SKU',
    'item-price' : 'Order Value',
    'discount' : 'Discount Amount',
    'shipping-price' : 'Shipping',
    'shipping-discount' : 'Shipping Discount',
    'item-tax' : 'Sales Tax',
    'order-net' : 'Order Net',
    'order-total' : 'Order Total',
    'card-fees' : 'Card Processing Fees',
    'adjusted-order-total' : 'Adjusted Order Total',
    'adjusted-card-processing-fees' : 'Adjusted Card Processing Fees',
    'adjusted-net-order-amount' : 'Adjusted Net Order Amount',
    # added during processing
    'title' : 'title',
    'weight' : 'weight',
    'category' : 'category',
    'brand' : 'brand',
    'vmdoption' : 'vmdoption',
}

QUANTITY_PATTERN = {
    'AmazonCOM' : r'^\(\d+\svnt.\)\s',
    'AmazonEU' : r'^\(\d+\svnt.\)\s',
    'Etsy' : r'^\d+\svnt.\s',
    }

TRACKED_LP_SHIPMENT_TYPE = {
    'VKS' : 'P2P_3_XS',
    'MKS' : 'P2P_3_S',
    'DKS' : 'P2P_3_M',
}

UNTRACKED_LP_SHIPMENT_TYPE = {
    'VKS' : 'P2P_1_XS',
    'MKS' : 'P2P_1_S',
    'DKS' : 'P2P_1_M',
}

TRACKED_INNER_SALES_CHANNELS = ['amazon.fr', 'amazon.it', 'amazon.es', 'amazon.com', 'amazon.ca', 'amazon.com.mx']

SKU_CATEGORY = {
    'WZ5': 'TAROT CARDS',
    'PAM36': 'TAROT CARDS',
    'SWT80': 'TAROT CARDS',
}

READ_EXCEL_CONFIG = {
    'SKU_MAPPING': {
        'wb_name': 'Amazon SKU Mapping.xlsx',
        'ws_name': 'Mapping',
        'start_row': 2,
        'check_integrity': True,
        'alert_for_duplicates': True,
        },
    'SKU_BRAND': {
        'wb_name': 'Storage.xlsm',
        'ws_name': 'Storage',
        'start_row': 1,
        'check_integrity': False,
        'alert_for_duplicates': False,
    },
}


if __name__ == '__main__':
    pass