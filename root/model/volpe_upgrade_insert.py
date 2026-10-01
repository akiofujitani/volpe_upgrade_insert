import logging
import pyautogui
import keyboard
from win32 import win32gui
from time import sleep
from threading import Event
from os.path import join
from .scripts.file_handler import file_list, csv_to_list
from .scripts import erp_volpe_handler, win_handler
from .database import Database
from .classes.config import Configuration, CSV_Path
from .classes.upgrade import Upgrade, UpgradeList
from ctypes import Union

logger = logging.getLogger('white_label_unlock')

IMG_PATH = 'Images/Registry'


def get_close_message_box(title: str, command: str, wait_time: int=10) -> bool:
    '''
    get the ERP message box and closes it.
    Is expecting the message box title and the command to closes it.    
    ''' 
    for _ in range(wait_time):
        pyautogui.failSafeCheck()
        active_window = win32gui.GetForegroundWindow()
        win_title = win32gui.GetWindowText(active_window)
        if title in win_title:
            sleep(0.5)
            keyboard.press_and_release(command)
            sleep(0.5)
            return True
        sleep(1)
    return False


def filter_upgrade(upgrade: str) -> None:
    pass


def insert_values(customer_list: list[str], upgrade_list: list[str], no_monitor: bool=True) -> None:
    try:
        for upgrade in upgrade_list:
            filter_upgrade(upgrade)
            code_column = win_handler.image_search('code_column.png') # temp
            row_pos = win_handler.image_search('arrow.pn') # temp
            id_value = erp_volpe_handler.ctrl_d(code_column.left, row_pos.top + 5)
            old_id_value = 0
            while not id_value == old_id_value:
                sleep(0.3)
                keyboard.press('a')
                '''
                get window and customer button

                click button
                confirm window
                ''' 
                for customer_code in customer_list:
                    pyautogui.write(customer_code)
                    sleep(0.3)
                    for _ in range(3):
                        keyboard.press('tab')
                        sleep(0.2)
                    keyboard.press('space')
                    sleep(0.5)
                    # search arrow image
                    if win_handler.image_search('arrow.png'):
                        keyboard.press('tab')
                        sleep(0.2)
                        keyboard.press('enter')
                        sleep(0.3)
                        keyboard.press_and_release('shift + tab')
                    for _ in range(3):
                        keyboard.press('shift + tab')
                        sleep(0.2)                    
                win_handler.icon_click('select.png')
                sleep(0.5)
                keyboard.press_and_release('alt + c')
                sleep(0.5)
                keyboard.press('down')
                old_id_value = id_value
                id_value = erp_volpe_handler.ctrl_d(code_column.left, row_pos.top + 5)
    except Exception as error:
        logger.error(f'Could not add customers due {error}')


    for customer_id, product_list in contents_by_customer.items():
        logger.info(f'Customer {customer_id}')
        codes_list = []
        current_values = current_list.get(customer_id)
        if current_values:
            codes_list = current_values.keys()
        for code, description in product_list.items():
            pyautogui.failSafeCheck()
            logger.info(f'{code} - {description}')
            if not code in codes_list:
                keyboard.press('i')
                sleep(0.5)
                pyautogui.write(code)
                sleep(0.3)
                pyautogui.press('tab')                
                if get_close_message_box('AVISO', 'space', 1):
                    pyautogui.hotkey('ctrl', 'a')
                    sleep(0.2)
                    pyautogui.press('backspace')
                    sleep(0.3)
                    keyboard.press_and_release('alt + c')
                    sleep(0.5)                    
                else:                    
                    pyautogui.write(customer_id)
                    sleep(0.3)
                    pyautogui.press('tab')           
                    if get_close_message_box('AVISO', 'space', 1):
                        pyautogui.hotkey('ctrl', 'a')
                        sleep(0.2)
                        pyautogui.press('backspace')
                        sleep(0.3)   
                        keyboard.press_and_release('alt + c')
                        sleep(0.5)
                        keyboard.press('s')
                        sleep(0.5)                                                                
                    keyboard.press_and_release('alt + o')
                    sleep(0.5)
                if get_close_message_box('AVISO', 'space', 1):
                    sleep(0.3)
                    keyboard.press_and_release('alt + c')
                    sleep(0.5)
                    keyboard.press('s')
                    sleep(0.5)
                pyautogui.failSafeCheck()
    return


def remove_values() -> None:
    pass


def description_ignore(description: str, ignore_list: list[str]) -> bool:
    for ignore_key in ignore_list:
        if ignore_key in description:
            return True
    return False


def filter_by_customer(csv_contents: list[dict[str, str]], ignore_list: list[str], customer_key: str, product_key: str, product_descr_key:str) -> dict[int, dict[str, str]]:
    contents_by_customer = {}
    for csv_line in csv_contents:
        customer_code = csv_line.get(customer_key)
        product_code = csv_line.get(product_key)
        product_description = csv_line.get(product_descr_key)
        if not description_ignore(product_description, ignore_list):
            if not customer_code in contents_by_customer.keys():
                new_contents = {}
                new_contents[product_code] = product_description
                contents_by_customer[customer_code] = new_contents
            else:
                contents = contents_by_customer.get(customer_code)
                if not product_code in contents.keys():
                    contents[product_code] = product_description
                contents_by_customer[customer_code] = contents
    return contents_by_customer


def load_csv(csv_in_path: str, csv_extension: str, csv_delimiter: str) -> list[dict[str, str]]:
    csv_path = csv_in_path
    files_list = file_list(csv_path, csv_extension)
    csv_contents = []
    if len(files_list) > 0:
        csv_contents_list = []
        for file in files_list:
            csv_contents = csv_to_list(join(csv_path, file), csv_delimiter)
            if csv_contents:
                csv_contents_list += csv_contents
    if len(csv_contents) > 0:
        return csv_contents


def load_csv(csv_path: str, extension: str, delimiter: str, header_dict: dict[str, str], object: Union[Upgrade, object]) -> list[Union[Upgrade, object]]:
    '''
    Load CSV
    --------

    
    '''
    file_list_data = file_list(csv_path, extension)
    object_list = []
    if len(file_list_data) > 0:
        for file in file_list_data:
            file_contents = csv_to_list(join(csv_path, file), delimiter)
            for content_line in file_contents:
                values_dict = {}
                for key, key_name in header_dict.items():
                    values_dict[key] = content_line.get(key_name.upper())
                new_object = object.init_dict(values_dict)
                if new_object:
                    object_list.append(new_object)
    return object_list


def load_upgrade_list(config: Configuration) -> UpgradeList:
    csv_upgrade_list: CSV_Path = config.csv_upgrade_list
    csv_upgrade_customer: CSV_Path = config.csv_upgrade_customer
    csv_upgrade_period: CSV_Path = config.csv_upgrade_period
    contents_upgrade_list = csv_to_list(csv_upgrade_list.csv_path, csv_upgrade_list.csv_delimiter)
    contents_upgrade_customer = csv_to_list(csv_upgrade_customer.csv_path, csv_upgrade_customer.csv_delimiter)
    contents_upgrade_period = csv_to_list(csv_to_list(csv_upgrade_period.csv_path, csv_upgrade_period, csv_upgrade_period.csv_delimiter))


def volpe_upgrade_insert_main(event: Event, config: Configuration) -> None:
    '''
    White label unlock main function
    --------------------------------
    

    '''
    # 1. load and proccess csv
    csv_contents = load_csv(config.csv_in_path.csv_path, config.csv_in_path.csv_extension, config.csv_in_path.csv_delimiter, Upgrade)
    csv_current_list = load_csv(config.csv_current_list.csv_path, config.csv_current_list.csv_extension, config.csv_current_list.csv_delimiter)
    csv_done = load_csv(config.csv_done_path.csv_path, config.csv_done_path.csv_extension, config.csv_done_path.csv_delimiter)


    # 2. Set volpe routine
    try:
        sleep(config.before_start_time)
        # erp_volpe_handler.volpe_back_to_main()
        # erp_volpe_handler.volpe_load_tab('Tab_sales', 'Icon_sell_parameter.png')
        # erp_volpe_handler.volpe_open_window('Icon_Product_upgrade.png', 'Title_product_upgrade.png', path=IMG_PATH)
    except Exception as error:
        logger.warning(f'Volpe error or not found {error}')

    # 3. start adding values
    try:
        insert_values()
    except Exception as error:
        logger.error(f'Error adding values due {error}')
    
    # 4. start removeing values
    try:
        remove_values()
    except Exception as error:
        logger.error(f'Error removing values due {error}')    


    # 4. end proccess



def volpe_upgrade_insert(database: Database, event: Event) -> None:
    try:
        config = database.config.get('config')
    except Exception as error:
        logger.critical(f'Could not load config file due {error}')
        event.set()
        return
    
    volpe_upgrade_insert_main(event, config)