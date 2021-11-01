from datetime import datetime
import platform
import logging
import shutil
import json
import sys
import os


def is_windows_machine() -> bool:
    '''returns True if machine executing the code is Windows based'''
    machine_os = platform.system()
    return True if machine_os == 'Windows' else False

def get_output_dir(client_file=True):
    '''returns target dir for output files depending on execution type (.exe/.py) and file type (client/systemic)'''
    # pyinstaller sets 'frozen' attr to sys module when compiling
    if getattr(sys, 'frozen', False):
        curr_folder = os.path.dirname(sys.executable)
    else:
        curr_folder = os.path.dirname(os.path.abspath(__file__))
    return get_level_up_abspath(curr_folder) if client_file else curr_folder

def get_level_up_abspath(absdir_path:str) -> str:
    '''returns abs directory path one level above provided dir as arg'''
    return os.path.dirname(absdir_path)

def create_src_file_backup(target_file_abs_path:str, backup_fname_prefix:str) -> str:
    '''returns abspath of created file backup'''
    src_files_folder = get_src_files_folder()
    _, backup_ext = os.path.splitext(target_file_abs_path)
    backup_abspath = get_backup_f_abspath(src_files_folder, backup_fname_prefix, backup_ext)
    shutil.copy(src=target_file_abs_path, dst=backup_abspath)
    logging.info(f'Backup created at: {backup_abspath}')
    return backup_abspath

def get_src_files_folder():
    output_dir = get_output_dir(client_file=False)
    target_dir = os.path.join(output_dir, 'src files')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
        logging.debug(f'src files directory inside Helper files has been recreated: {target_dir}')
    return target_dir

def get_backup_f_abspath(src_files_folder:str, backup_fname_prefix:str, ext:str) -> str:
    '''returns abs path for backup file. fname format: backup_fname_prefix-YY-MM-DD-HH-MM.ext'''
    timestamp = datetime.now().strftime('%y-%m-%d %H-%M')
    backup_fname = f'{backup_fname_prefix} {timestamp}{ext}'
    return os.path.join(src_files_folder, backup_fname)

def dump_to_json(export_obj, json_fname:str) -> str:
    '''exports export_obj to json file. Returns path to crated json'''
    output_dir = get_output_dir(client_file=False)
    json_path = os.path.join(output_dir, json_fname)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(export_obj, f, indent=4)
    return json_path

def read_json_to_obj(json_file_path:str):
    '''reads json file and returns python object'''
    with open(json_file_path, 'r', encoding='utf-8') as f:
        orders = json.load(f)
    return orders

def delete_file(file_abspath:str):
    '''deletes file located in file_abspath'''
    try:
        os.remove(file_abspath)
    except FileNotFoundError:
        logging.warning(f'Tried deleting file: {file_abspath}, but apparently human has taken care of it first. (File not found)')
    except Exception as e:
        logging.warning(f'Unexpected err: {e} while flushing db old records, deleting file: {file_abspath}')


if __name__ == '__main__':
    pass