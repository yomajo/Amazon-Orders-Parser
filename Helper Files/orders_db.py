import sqlite3
from datetime import datetime, date
from random import choices
import string
from time import sleep

# GLOBAL VARIABLE
ORDERS_ARCHIVE_DAYS = 14
DATABASE_PATH = 'amzn_orders.db'
BACKUP_DB_NAME = 'amzn_orders_backup-fridaytest.db'

def create_schema(con):
    # Creating first 'program_runs' table:
    try:
        with con:
            con.execute('''CREATE TABLE program_runs (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                run_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                                weekday INTEGER);''')
    except sqlite3.OperationalError as e:
        print(f'program_runs table already created. Error: {e}')
        pass
    # Creating second 'orders' table:
    try:
        with con:
            con.execute('''CREATE TABLE orders (order_id TEXT PRIMARY KEY,
                                            purchase_date TEXT,
                                            payments_date TEXT,
                                            buyer_name TEXT NOT NULL,
                                            last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                            date_added TEXT NOT NULL,
                                            run INTEGER NOT NULL,
                                            FOREIGN KEY (run) REFERENCES program_runs (id) ON DELETE CASCADE);''')
    except sqlite3.OperationalError as e:
        print(f'orders table already created. Error: {e}')
        pass
    print('database tables are in place and ready to be used')

def drop_tables(con):
    try:
        with con:
            con.execute('''DROP TABLE orders''')
            con.execute('''DROP TABLE program_runs''')
    except Exception as e:
        print(f'failed to delete tables. Error {e}')
    print('tables deleted')

def insert_new_run(con, weekday, run_time_default = True):
    '''run_time_default = True adds SQL timestamp in db automatically. However manual timestamp in format:
    'YYYY-MM-DD HH:MM:SS' could be added'''
    try:
        with con:
            if run_time_default == True:
                con.execute('''INSERT INTO program_runs (weekday) VALUES (:weekday)''', {'weekday' : weekday})
                print(f'Added new run to program_runs table. Inserted with weekday: {weekday}')
            else:
                con.execute('''INSERT INTO program_runs (run_time, weekday) VALUES (
                        :run_time, :weekday)''', {'run_time' : run_time_default, 'weekday' : weekday})
                print(f'Added new run to program_runs with hardcoded run_time: {run_time_default}. Inserted with weekday: {weekday}')                
    except:
        print('failed to insert, catch me.')


def get_all_tables(con):
    print('Getting all tables in database:')
    try:
        with con:
            cur = con.cursor()
            cur.execute('''SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ''')
            results = cur.fetchall()
            print(results)
    except:
        print('failed get all tables, catch me.')

def fetch_orders(con, order_by_last_update=False):
    try:
        with con:
            cur = con.cursor()
            if order_by_last_update:   
                cur.execute('''SELECT * FROM orders ORDER BY last_update DESC''')
            else:
                cur.execute('''SELECT * FROM orders''')
            results = cur.fetchall()
            for row in results:
                print(row)
    except:
        print('failed to retrieve data from orders table, catch me.')

def get_current_run(con):
    try:
        with con:
            cur = con.cursor()
            cur.execute('''SELECT id, run_time FROM program_runs ORDER BY run_time DESC LIMIT 1''')
            run_id, run_time = cur.fetchone()
            run_time_date = run_time.split(' ')[0]
            # Validaring the new run was made today (miliseconds before)
            assert run_time_date == datetime.today().strftime('%Y-%m-%d')
            print(f'Returning new run id: {run_id}')
            return run_id
    except sqlite3.OperationalError as e:
        print(f'Syntax error in query trying to fetch current run. Error: {e}')

def get_today_weekday_int(date_arg=date.today()):
    '''returns integer for provided date (defaults to today). Monday - 1, ..., Sunday - 7'''
    return datetime.weekday(date_arg) + 1

def get_random_code():
    choose_from = string.ascii_uppercase + string.digits
    return ''.join(choices(choose_from, k=8)) + '-' + ''.join(choices(choose_from, k=8))

def insert_new_order(con, order_id, purchase_date, payments_date, buyer_name, run_id):
    date_added = date.today().strftime('%Y-%m-%d')
    try:
        with con:
            con.execute('''INSERT INTO orders (order_id, purchase_date, payments_date, buyer_name, date_added, run)
                                            VALUES (:order_id, :purchase_date, :payments_date, :buyer_name, :date_added, :run)''',
                                            {'order_id':order_id, 'purchase_date':purchase_date, 'payments_date':payments_date,
                                            'buyer_name':buyer_name, 'date_added':date_added, 'run':run_id})
        print(f'Data for order {order_id} in run {run_id} inserted successfully.')
    except sqlite3.OperationalError as e:
        print(f'Data insertion failed. Syntax error: {e}')
    except Exception as e:
        print(f'Unknown error while inserting data to orders table. Error: {e}')

def add_multiple_orders(con, run_id):
    for i in range(10):
        buyer = 'Friday_' + str(i)
        purchase_date = '2020-02-25'
        payments_date = '2020-03-01'
        order_id = get_random_code()
        print(f'Sleeping for 2 before inserting new entry. Currently loop number: {i}')
        sleep(2)
        insert_new_order(con, order_id, purchase_date, payments_date, buyer, run_id)

def get_old_runs_id_lst(con, archive_days=ORDERS_ARCHIVE_DAYS) -> list:
    try:
        with con:
            cur = con.cursor()
            cur.execute('''SELECT id FROM program_runs WHERE
                        CAST(julianday('now', 'localtime') - julianday(run_time) AS INTEGER) >
                        :archive_days;''', {'archive_days':archive_days})
            results = cur.fetchall()
            cur.close()
        return [run_row[0] for run_row in results]
    except sqlite3.OperationalError as e:
        print(f'Failed to retrieve ids from program_runs table. Syntax error: {e}')

def get_list_order_ids_in_db(con):
    try:
        with con:
            cur = con.cursor()
            cur.execute('''SELECT order_id FROM orders''')
            results = cur.fetchall()
            cur.close()
        return [order_row[0] for order_row in results]
    except sqlite3.OperationalError as e:
        print(f'Failed to retrieve ids from orders table. Syntax error: {e}')

def flush_old_orders(con):
    del_run_ids = get_old_runs_id_lst(con, ORDERS_ARCHIVE_DAYS)
    try:
        with con:
            for run_id in del_run_ids:
                con.execute('''DELETE FROM program_runs WHERE id = :run''', {'run':run_id})
        print(f'Deleted orders (cascade) from orders table where run_id = {del_run_ids}')
    except sqlite3.OperationalError as e:
        print(f'Orders could not be deleted, passed run_ids: {del_run_ids}. Syntax error: {e}')
    except Exception as e:
        print(f'Unknown error while deleting orders to orders table based on run_ids {del_run_ids}. Error: {e}')
    
def friday_backup_db(con, backup_db_name = BACKUP_DB_NAME):
    if get_today_weekday_int() == 5:
        back_con = sqlite3.connect(backup_db_name)
        with back_con:
            con.backup(back_con, pages=0, name='main')
        back_con.close()
        print(f'It\'s Friday. New database backup was created at: {backup_db_name}')

def run():
    con = sqlite3.connect(DATABASE_PATH)
    con.execute("PRAGMA foreign_keys = 1")
    print('Connection initialized...')    
    # get_all_tables(con)
    # drop_tables(con)
    create_schema(con)

    # insert_new_run(con, get_today_weekday_int(), '2020-05-08 10:05:46')
    # new_run_id = get_current_run(con)
    # get_all_tables(con)
    # add_multiple_orders(con, new_run_id)

    flush_old_orders(con)
    fetch_orders(con, order_by_last_update=False)
    # orders_in_db = get_list_order_ids_in_db(con)
    friday_backup_db(con, BACKUP_DB_NAME)
    print(f'Closing connection to database.')
    con.close()

if __name__ == "__main__":
    run()