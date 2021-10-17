from amzn_parser_utils import get_output_dir, create_src_file_backup, read_json_to_obj, delete_file
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.schema import ForeignKey
import datetime
import logging
import os
import shutil


# GLOBAL VARIABLES
ORDERS_ARCHIVE_DAYS = 60
# ORDERS_ARCHIVE_DAYS = 30
DATABASE_NAME = 'orders.db'
BACKUP_DB_BEFORE_NAME = 'orders_b4lrun.db'
BACKUP_DB_AFTER_NAME = 'orders_lrun.db'
VBA_ERROR_ALERT = 'ERROR_CALL_DADDY'

Base = declarative_base()


class ProgramRun(Base):
    '''database table model representing unique program run'''
    __tablename__ = 'program_run'

    def __init__(self, fpath:str, timestamp=datetime.datetime.now()):
        self.fpath = fpath
        self.timestamp = timestamp

    id = Column(Integer, primary_key=True, nullable=False)
    fpath = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=False), default=datetime.datetime.now())
    orders = relationship('Order', cascade='all, delete', cascade_backrefs=True,
                passive_deletes=False, passive_updates=False, backref='run_obj')

    def __repr__(self) -> str:
        return f'<ProgramRun id: {self.id}, timestamp: {self.timestamp}, fpath: {self.fpath}>'
    

class Order(Base):
    '''database table model representing Order'''
    __tablename__ = 'order'

    def __init__(self, order_id, purchase_date, buyer_name, run, sales_channel):
        self.order_id = order_id
        self.purchase_date = purchase_date
        self.buyer_name = buyer_name
        self.run = run
        self.sales_channel = sales_channel

    order_id = Column(String, primary_key=True, nullable=False)
    purchase_date = Column(String)
    buyer_name = Column(String)
    sales_channel = Column(String, nullable=False)      # AmazonEU / AmazonCOM / Etsy
    run = Column(Integer, ForeignKey('program_run.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    def __repr__(self) -> str:
        return f'<Order order_id: {self.order_id}, added on run: {self.run}>'


class SQLAlchemyOrdersDB:
    '''Orders Database management. Two main methods:

    get_new_orders_only() - from passed orders to cls returns only ones, not yet in database.
    Expected to be called outside of this cls to get self.new_orders var.

    add_orders_to_db() - pushes new orders (returned list from get_new_orders_only() method)
    selected data to database, performs backups before and after each run, periodic flushing of old entries 
    
    Arguments:

    orders - list of dict / OrderedDict's

    source_file_path - abs path to source file for orders (Amazon / Etsy)

    sales_channel - str identifier for db entry, backup file naming. Expected value: ['AmazonEU', 'AmazonCOM', Etsy]

    testing - optional flag for testing (suspending backup, save add source_file_path to program_run table instead)
    '''

    def __init__(self, orders:list, source_file_path:str, sales_channel:str, testing=False):
        self.orders = orders
        self.source_file_path = source_file_path
        self.sales_channel = sales_channel
        self.testing = testing
        self.__setup_db()
        self._backup_db(self.db_backup_b4_path)
        self.session = self.get_session()

    def __setup_db(self):
        self.__get_db_paths()
        if not os.path.exists(self.db_path):
            self.__get_engine()
            Base.metadata.create_all(bind=self.engine)
            print('------ database has been created (change to logging) ------')
        else:
            print('------ database already exists (change to logging) ------')

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

    def add_orders_to_db(self, test_timestamp):
        '''filters passed orders to cls to only those, whose order_id
        (db table unique constraint) is not present in db yet adds them to db
        assumes get_new_orders_only was called outside of this cls before to get self.new_orders'''
        try:
            if self.new_orders:
                self._add_new_orders_to_db(self.new_orders, test_timestamp)
                self.flush_old_records()
                self._backup_db(self.db_backup_after_path)
            # create backup with new added orders 
            logging.debug(f'New orders added, flushing old records complete, backup after created at: {self.db_backup_after_path}')
            return len(self.new_orders)
        except Exception as e:
            logging.critical(f'Unexpected err {e} trying to add orders to db. Alerting VBA, terminating program immediately.')
            print(VBA_ERROR_ALERT)
            exit()

    def _add_new_orders_to_db(self, new_orders:list, test_timestamp):
        '''create new entry in program_runs table, add new orders'''
        self.new_run_id = self._add_new_run(test_timestamp)
        added_to_db_counter = 0
        for order in new_orders:
            self._add_single_order(order)
            added_to_db_counter += 1
        self.session.commit()
        print(f'Total {added_to_db_counter} new orders have been added to database')

    def _add_single_order(self, order_dict:dict):
        '''CONTAINS HARDCODED VALUES WARNING SOLVE LATER. Different keys for etsy, WARNING'''        
        new_order = Order(order_id=order_dict['order-id'],
                purchase_date=order_dict['purchase-date'],
                buyer_name=order_dict['buyer-name'],
                run=self.new_run_id,
                sales_channel=self.sales_channel)
        self.session.add(new_order)

    def _add_new_run(self, test_timestamp) -> int:
        '''adds new row in program_run table, returns new run id,
        creates source file backup, saves its path. On testing - save original file path'''
        backup_path = self.source_file_path if self.testing else create_src_file_backup(self.source_file_path, self.sales_channel)
        print(f'This is backup path being saved to program_run: {backup_path}')
        new_run = ProgramRun(backup_path, test_timestamp)
        self.session.add(new_run)
        self.session.commit()
        logging.debug(f'Added new run: {new_run}, created backup')
        return new_run.id

    def get_new_orders_only(self) -> list:
        '''From passed orders to cls, returns only orders NOT YET in database WARNING DIFFERENT KEYS FOR ETSY DICT
        order-id vs Order ID SOLVE LATER
        called from main.py'''
        orders_in_db = self._get_order_ids_in_db()
        self.new_orders = [order_data for order_data in self.orders if order_data['order-id'] not in orders_in_db]
        logging.info(f'Returning {len(self.new_orders)}/{len(self.orders)} new/loaded orders for further processing')
        return self.new_orders

    def _get_order_ids_in_db(self) -> list:
        '''returns a list of order ids currently present in 'orders' database table'''
        order_id_lst_in_db = [order_obj.order_id for order_obj in self.session.query(Order).all()]
        logging.debug(f'Before inserting new orders, orders table contains {len(order_id_lst_in_db)} entries')
        return order_id_lst_in_db

    def flush_old_records(self):
        '''deletes old runs, associated backup files and orders (deleting runs delete cascade associated orders)'''
        old_runs = self._get_old_runs()
        try:
            for run in old_runs:
                orders_in_run = self.session.query(Order).filter_by(run_obj=run).all()
                logging.info(f'Deleting {len(orders_in_run)} orders associated with old {run} and backup file: {run.fpath}')
                delete_file(run.fpath)   
                self.session.delete(run)
            self.session.commit()
        except Exception as e:
            logging.warning(f'Unexpected err while flushing old records from db inside flush_old_records. Err: {e}. Last recorded run {run}')

    def _get_old_runs(self):
        '''returns runs that were added ORDERS_ARCHIVE_DAYS (global var) or more days ago'''
        delete_before_this_timestamp = datetime.datetime.now() - datetime.timedelta(days=ORDERS_ARCHIVE_DAYS)        
        runs = self.session.query(ProgramRun).filter(ProgramRun.timestamp < delete_before_this_timestamp).all()
        return runs

    def _backup_db(self, backup_db_path):
        '''creates database backup file at backup_db_path'''
        try:
            shutil.copy(src=self.db_path, dst=backup_db_path)
            logging.info(f"New database backup {os.path.basename(backup_db_path)} created on: "
                        f"{datetime.datetime.today().strftime('%Y-%m-%d %H:%M')} location: {backup_db_path}")
        except Exception as e:
            raise e

def run():
    f1 = r'C:\Coding\Amazon Orders Parser\Helper Files\testing_orders1.json'
    f2 = r'C:\Coding\Amazon Orders Parser\Helper Files\testing_orders2.json'
    f3 = r'C:\Coding\Amazon Orders Parser\Helper Files\testing_orders3.json'
    orders_1 = read_json_to_obj(f1)
    # orders_2 = read_json_to_obj(f2)
    # orders_3 = read_json_to_obj(f3)

    db = SQLAlchemyOrdersDB(orders_1, f1, 'AmazonEU', testing=True)
    # hardcoded_timestamp1 = datetime.datetime(2021, 9, 15, 10, 58, 39)
    # db.add_orders_to_db(hardcoded_timestamp1)

    # db2 = SQLAlchemyOrdersDB(orders_2, f2, 'AmazonCOM', testing=False)
    # hardcoded_timestamp2 = datetime.datetime(2021, 6, 10, 6, 00, 15)
    # db2.add_orders_to_db(hardcoded_timestamp2)

    # db3 = SQLAlchemyOrdersDB(orders_3, f3, 'Etsy', testing=False)
    # hardcoded_timestamp3 = datetime.datetime(2021, 10, 4, 20, 5, 6)
    # db3.add_orders_to_db(hardcoded_timestamp3)

    
    # session = db.get_session()

    # rename 2 run id to -> 20
    # run = session.query(ProgramRun).filter_by(id=2).first()
    # run.id = 20
    # print(f'Changed run 2 id to 20. Expecting orders to inherit new val')
    # session.commit()

    # # # view changes
    # run_after_changes = session.query(ProgramRun).filter_by(id=20).first()
    # print(run_after_changes)

    # db_order_objs = session.query(Order).all()
    # for order_obj in db_order_objs:
    #     print(order_obj)

    # print(f'Total orders in db: {len(db_order_objs)}') #21

    # run1_db_orders = session.query(Order).filter(Order.run == 1).all()
    # run2_db_orders = session.query(Order).filter(Order.run == 2).all()
    # run3_db_orders = session.query(Order).filter(Order.run == 3).all()

    # print(f'1 run contains {len(run1_db_orders)} orders')   #6
    # print(f'2 run contains {len(run2_db_orders)} orders')   #10 - will be deleted
    # print(f'3 run contains {len(run3_db_orders)} orders')   #5

    db_order_objs = db.session.query(Order).all()
    for order_obj in db_order_objs:
        print(order_obj)
    print(f'Total {len(db_order_objs)} orders left in db')
    

if __name__ == '__main__':
    run()