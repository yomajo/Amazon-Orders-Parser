from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime

from amzn_parser_utils import get_output_dir, create_src_file_backup
from datetime import datetime
import logging
import os


# GLOBAL VARIABLES
ORDERS_ARCHIVE_DAYS = 60
DATABASE_NAME = 'orders.db'
BACKUP_DB_BEFORE_NAME = 'orders_b4lrun.db'
BACKUP_DB_AFTER_NAME = 'orders_lrun.db'
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'

Base = declarative_base()

random_order = {'order-id': '666-9999999-4474765',
        'order-item-id': '56464121458723',
        'purchase-date': '2021-02-01T06:00:20+00:00',
        'payments-date': '2021-04-22T07:00:41+00:00',
        'buyer-email': 'vhl9djsd99qq6g6@marketplace.amazon.de',
        'buyer-name': 'Namer Namerson',
        'buyer-phone-number': '00436763420904',
        'sku': 'OR21',
        'product-name': 'Earth Wisdom Oracle',
        'quantity-purchased': '1',
        'currency': 'EUR',
        'item-price': '19.89',
        'item-tax': '3.45',
        'shipping-price': '0.00',
        'shipping-tax': '0.00',
        'ship-service-level': 'Standard',
        'recipient-name': 'Ulrike Brichta',
        'ship-address-1': 'Steinbachstraße 93',
        'ship-address-2': '',
        'ship-address-3': '',
        'ship-city': 'Mauerbach',
        'ship-state': '',
        'ship-postal-code': '3001',
        'ship-country': 'AT',
        'ship-phone-number': '+436763420904',
        'delivery-start-date': '',
        'delivery-end-date': '',
        'delivery-time-zone': '',
        'delivery-Instructions': '',
        'sales-channel': 'Amazon.de',
        'is-business-order': 'false',
        'purchase-order-number': '',
        'price-designation': '',
        'shipment-status': '',
        'is-sold-by-ab': 'false'}


class ProgramRun(Base):
    '''database table model representing unique program run'''
    __tablename__ = 'program_run'

    def __init__(self, fpath:str):
        self.fpath = fpath

    id = Column(Integer, primary_key=True, nullable=False)
    fpath = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=False), default=datetime.now())
    orders = relationship('Order', cascade='all, delete', passive_deletes=True)

    def __repr__(self) -> str:
        return f'<ProgramRun id: {self.id}, timestamp: {self.timestamp}, fpath: {self.fpath}>'
    

class Order(Base):
    '''database table model representing Order'''
    __tablename__ = 'order'

    def __init__(self, order_id, purchase_date, buyer_name, date_added, run, sales_channel):
        self.order_id = order_id
        self.purchase_date = purchase_date
        self.buyer_name = buyer_name
        self.date_added = date_added
        self.run = run
        self.sales_channel = sales_channel

    order_id = Column(String, primary_key=True, nullable=False)
    purchase_date = Column(String)
    buyer_name = Column(String)
    date_added = Column(String)
    sales_channel = Column(String, nullable=False)      # AmazonEU / AmazonCOM / Etsy
    run = Column(Integer, ForeignKey('program_run.id'))

    def __repr__(self) -> str:
        return f'<Order order_id: {self.order_id}, added on run: {self.run}>'


class SQLAlchemyOrdersDB:
    '''EDIT DOCSTRING
    
    Arguments:
    orders - list of dict / OrderedDict's
    source_file_path - abs path to source file for orders (Amazon / Etsy)
    sales_channel - str identifier for db entry, backup file naming. Expected values: ['AmazonEU', 'AmazonCOM', Etsy]
    testing - optional flag for testing (suspending backup)
    '''

    def __init__(self, orders:list, source_file_path:str, sales_channel:str, testing=False):
        self.orders = orders
        self.source_file_path = source_file_path
        self.testing = testing
        self.__setup_db()
        self.session = self.get_session()

    def __setup_db(self):
        self.__get_db_paths()
        if not os.path.exists(self.db_path):
            self.__get_engine()
            Base.metadata.create_all(bind=self.engine)
            print('------ database has been created ------')
        else:
            print('------ database already exists ------')

    def __get_db_paths(self):
        output_dir = get_output_dir(client_file=False)
        self.db_path = os.path.join(output_dir, DATABASE_NAME)
        self.db_backup_b4_path = os.path.join(output_dir, BACKUP_DB_BEFORE_NAME)
        self.db_backup_after_path = os.path.join(output_dir, BACKUP_DB_AFTER_NAME)

    def __get_engine(self):
        engine_path = f'sqlite:///{self.db_path}'
        self.engine = create_engine(engine_path, echo=False)
    
    def get_session(self):
        '''returns database session object to work outside the scope of class. For example querying'''
        self.__get_engine()
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

        
    def add_one_order_to_db_external_use(self, order_dict:dict):
        print('creating order in Order table') 
        new_run_id = self._add_new_run()

        order_id = order_dict['order-id']
        purchased = order_dict['purchase-date']
        buyer_name = order_dict['buyer-name']
        date_added = '2021-10-15'
        
        new_order = Order(order_id=order_id,
                purchase_date=purchased,
                buyer_name=buyer_name,
                date_added=date_added,
                run=new_run_id,
                sales_channel='AmazonCOM')

        self.session.add(new_order)
        self.session.commit()
        print('order added to db')


    def add_new_orders_to_db(self):
        '''WARNING SOLVE LATER : only new orders to be added to db'''
        self.new_run_id = self._add_new_run()
        # add all passed orders to db class for now.
        for order in self.orders:
            try:
                self._add_single_order(order)
                print('debug log - add individual order_id')
            except Exception as e:
                print(f'Failed to add order: {order} \nto database. Warn VBA, try adding rest of orders. Err: {e}')
                continue
        self.session.commit()
        print('Total ??? new orders have been added to database')


    def _add_single_order(self, order_dict:dict):
        '''CONTAINS HARDCODED VALUES WARNING SOLVE LATER'''        
        new_order = Order(order_id=order_dict['order-id'],
                purchase_date=order_dict['purchase-date'],
                buyer_name=order_dict['buyer-name'],
                date_added='2021-10-15',
                run=self.new_run_id,
                sales_channel='AmazonCOM')
        self.session.add(new_order)
        print('product added to db')


    def _add_new_run(self) -> int:
        new_run = ProgramRun(self.source_file_path)
        self.session.add(new_run)
        self.session.commit()
        print(f'Returning new run id: {new_run.id}')
        return new_run.id


    def get_new_orders_only(self) -> list:
        '''From passed orders to cls, returns only orders NOT YET in database WARNING DIFFERENT KEYS FOR ETSY DICT
        order-id vs Order ID SOLVE LATER
        '''
        orders_in_db = self._get_order_ids_in_db()
        self.new_orders = [order_data for order_data in self.orders if order_data['order-id'] not in orders_in_db]
        logging.info(f'Returning {len(self.new_orders)}/{len(self.orders)} new/loaded orders for further processing')
        return self.new_orders


    def _get_order_ids_in_db(self) -> list:
        '''returns a list of order ids currently present in 'orders' database table'''
        order_id_lst_in_db = [order_obj.order_id for order_obj in self.session.query(Order).all()]
        logging.debug(f'Before inserting new orders, orders table contains {len(order_id_lst_in_db)} entries')
        return order_id_lst_in_db


def run():

    # testing_file = r'C:\Coding\Amazon Orders Parser\Helper Files\sampleEU.txt'
    testing_file = r'C:\Coding\Amazon Orders Parser\Helper Files\sampleetsy.csv'
    create_src_file_backup(testing_file, 'AmazonEU')
    # db = SQLAlchemyOrdersDB(orders=['order1', 'order2'], source_file_path=testing_file, testing=True)
    # db_session = db.get_session()
    # db._add_single_order(random_order)
    # runs = db_session.query(ProgramRun).all()
    # for run in runs:
    #     print(run.id, run.timestamp)

folder_name = 'src files'
    
    # for order in orders_in_db:
    #     print(f'Order with id: {order.order_id} has been added in run: {order.run}')





if __name__ == '__main__':
    run()