import logging
import pyautogui
import keyboard
from win32 import win32gui
from time import sleep
from threading import Event
from os.path import join
from .scripts.file_handler import file_list, csv_to_list
from .scripts import erp_volpe_handler
from .database import Database
from .classes.config import Configuration


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


def insert_values(contents_by_customer: dict[str, dict[str, str]], current_list: dict[str, dict[str, str]], no_monitor: bool=True) -> None:
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
    if len(files_list) > 0:
        csv_contents_list = []
        for file in files_list:
            csv_contents = csv_to_list(join(csv_path, file), csv_delimiter)
            if csv_contents:
                csv_contents_list += csv_contents
    if len(csv_contents) > 0:
        return csv_contents


def white_label_unlock_main(event: Event, config: Configuration) -> None:
    '''
    White label unlock main function
    --------------------------------
    

    '''
    # 1. load and proccess csv
    csv_contents = load_csv(config.csv_in_path, config.csv_extension, config.csv_delimiter)
    csv_current_list = load_csv(config.csv_current_list, config.csv_extension, config.csv_delimiter)
    current_list = filter_by_customer(csv_current_list, [], 'CLIENTE', 'PRODUTO', 'DESCRIÇÃO')
    contents_by_customer = filter_by_customer(csv_contents, config.ignore_list, 'CÓD.CLI.', 'CÓD.PRO.', 'DESCRIÇÃO')


    # 2. Set volpe routine
    try:
        sleep(config.before_start_time)
        erp_volpe_handler.volpe_back_to_main()
        erp_volpe_handler.volpe_load_tab('Tab_reg', 'Icon_Reg_par.png')
        erp_volpe_handler.volpe_open_window('Icon_product_customer_x_white_label.png', 'Title_customer_x_white_label.png', path=IMG_PATH)
    except Exception as error:
        logger.warning(f'Volpe error or not found {error}')

    # 3. start adding values
    try:
        insert_values(contents_by_customer, current_list)
    except Exception as error:
        logger.error(f'Error adding values {error}')
    
    # 4. end proccess



def white_label_unlock(database: Database, event: Event) -> None:
    try:
        config = database.config.get('config')
    except Exception as error:
        logger.critical(f'Could not load config file due {error}')
        event.set()
        return
    
    white_label_unlock_main(event, config)