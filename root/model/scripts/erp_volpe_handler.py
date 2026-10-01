import pyautogui, keyboard, tkinter, datetime, os, pyscreeze, logging
from win32 import win32gui
from pyautogui import Point
from . import win_handler, file_handler, log_builder
from time import sleep
from .ocr_text_reader import return_text
from ntpath import join


logger = logging.getLogger('erp_volpe_handler')


def volpe_login(volpe_path: str, user_name=str, password=str):
    '''
    Login on ERP Volpe
    '''
    win_handler.run_application(volpe_path, 'volpe.exe')
    sleep(5)
    try:
        win_handler.loading_wait('Volpe_login.png')
        sleep(0.3)
        user_pos = win_handler.image_search('Volpe_login_user.png')
        pyautogui.doubleClick(user_pos.left + user_pos.width + 20, user_pos.top + 15)
        sleep(0.5)
        pyautogui.write(user_name)
        sleep(0.3)
        pass_pos = win_handler.image_search('Volpe_login_pass.png')
        pyautogui.doubleClick(pass_pos.left + pass_pos.width + 20, pass_pos.top + 15)
        sleep(0.5)
        pyautogui.write(password)
        sleep(0.3)
        win_handler.icon_click('Ok_button.png')
        win_handler.loading_wait('Volpe_Raiz_user.png')
        sleep(1)
        logger.info(f'Login done to user {user_name}')
        return
    except Exception as error:
        logger.error(f'volpe_login error {error}')
        raise(f'Login error {error}')


def prog_maint_open_fill_os(os_number, path='images') -> str:
    '''
    check window opened
    seearch of
    '''
    win_handler.image_search('Windows_Prog_Tec_man.png', path=path)
    os_field_pos = win_handler.image_search('Nro_da_OS.png', path=path)
    win_handler.click_field(os_field_pos, 'Bellow', distanceY=5)
    pyautogui.write(os_number)
    sleep(0.3)
    for _ in range(2):
        pyautogui.press('enter')
        sleep(0.3)
    row_text = get_volpe_row('Volpe_Prog_tec_Main_row.png', path=path)
    if not row_text[0][0:4] == os_number:
        raise Exception('Wrong OS number')
    # identify os. if not find return.
    logger.info(f'OS {os_number} confirmed.')
    os_status_pos = win_handler.image_search('OS_Status_Table.png', path=path)
    win_handler.click_field(os_status_pos, 'Bellow', distanceY=13)
    status = ctrl_d(os_status_pos.left + 20, os_status_pos.top + 20)
    if not status == 'CONCLUIDA':
        os_message = 'OS number is not concluded'
        logger.info(os_message)
        raise Exception(os_message)
    return row_text


def get_text_square(left=int, top=int, width=int, height=int):
    row_text = return_text({'top' : top, 'left' : left, 'width' : width, 'height' : height}, True)
    logger.info(row_text)
    return row_text 


def get_volpe_row(row_image=str, region_start=None , path='Images') -> str:
    '''
    Retrieve values from row using OCR processing
    '''
    try:
        window_size = win_handler.get_window_size()
        table_header = win_handler.image_search(row_image, region=(region_start), path=path)
        start_pos = Point(table_header.left, table_header.top + table_header.height)
        selec_pos = win_handler.image_search('Volpe_Table_selected.png', confidence_value=0.9, region=(start_pos.x - 15, start_pos.y, table_header.width, window_size.height - start_pos.y), path=path)            
        row_text = return_text({'top' : selec_pos.top, 'left' : selec_pos.left, 'width' : window_size.width, 'height' : 19}, True)  
        return row_text, selec_pos 
    except Exception as error:
        logger.error(f'get_volpe_row error {error}')
        raise error


def region_definer(raw_x, raw_y, width=None, height=None):
    '''
    Specic for image_search, translate position and return tuple with left, top, width and height
    '''
    windows_size = win_handler.get_window_size()
    start = Point(raw_x, raw_y)
    logger.info(f'{start.x} x {start.y}')
    return (int(start.x), int(start.y), windows_size.width if not width else width, windows_size.height if not height else height)


def enter_appointments():
    row_text, selec_pos = get_volpe_row('Volpe_Prog_Tec_Appoint_Table_Header_Start.png')
    pyautogui.moveTo(selec_pos.left + 50, selec_pos.top + 50)
    sleep(0.3)
    pyautogui.click(button='right')
    sleep(0.3)
    pyautogui.write('c')
    appoint = win_handler.image_search('Volpe_Apontamentos.png')
    return appoint


def volpe_tab_select(tab_name = str, confidence_value=0.8, confidence_reduction_step = 0.05, path='images'):
    '''
    tab searck and selection
    confidence values are still not completed tested
    works with a few tries with high confidenve value to acheive the mininum of false positives    
    '''
    cursor_pos = pyautogui.position()
    try:
        for _ in range(4):
            try:
                tab_pos = win_handler.image_search(f'{tab_name}.png', confidence_value, path=path)
                win_handler.click_volpe(tab_pos)
                pyautogui.moveTo(cursor_pos.x, cursor_pos.y),
                return
            except Exception as error:
                logger.debug(f'{tab_name} not found {error}')
            confidence_value = confidence_value - confidence_reduction_step
    except:
        logger.error(f'volpe_tab_select error {error}')
        raise Exception('Tab not found error')
    return


def ctrl_d(pos_x, pos_y):
    '''
    On ERP Volpe, retrive value from table where cursor clicked
    '''
    pyautogui.moveTo(pos_x, pos_y)
    pyautogui.click()
    sleep(0.5)
    pyautogui.hotkey('ctrl', 'd')
    sleep(0.3)
    copy_value = tkinter.Tk().clipboard_get()
    logger.debug(f'Field values: {copy_value}.')
    sleep(0.3)
    return copy_value


def is_int(value=str):
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_time(value=str):
    '''
    Check productivity hour values
    '''
    try:
        datetime.datetime.strptime(value, '%H:%M')
        return True
    except ValueError:
        return False


def appointments_value(text_string=str, tech_name_list=list):
    '''
    Organize values from string
    '''
    counter = 0
    organized_values = {}
    for line in text_string.split('\n'):
        if len(line) > 0:
            if is_int(line[0:4]):
                line_split = line.split(' ')
                organized_values['OS'] = line_split[0]
                organized_values['Date'] = line_split[1]
            if is_time(line):
                if counter == 0:
                    organized_values['Start'] = line
                    counter = counter + 1
                else:
                    organized_values['End'] = line
            if line in tech_name_list:
                organized_values['Technician'] = line
    return organized_values


def volpe_load_tab(tab_name, load_check_image):
    try:
        win_handler.activate_window('Volpe ')
        volpe_tab_select(tab_name)
        win_handler.loading_wait(load_check_image)
        sleep(0.3)
        return
    except Exception as error:
        logger.error(f'Volpe - load_tab error in {error}')
        raise error


def volpe_open_window(icon_name, window_name, path='Images', maximize=True):
    '''
    Open Volpe window by clicking in its icon, maximizing it later
    '''
    try:
        win_handler.icon_click(icon_name, path=path)
        sleep(0.5)
        win_pos = win_handler.image_search(window_name, path=path)
        sleep(1)
        if maximize:
            try:
                pyautogui.doubleClick(win_pos.left + 40, win_pos.top + 10)
                sleep(0.5)
                # pyautogui.press(['up', 'up'], interval=0.4)
                # pyautogui.press('enter')
                # win_handler.icon_click('Volpe_Maximize.png', confidence_value=0.6, region_value=(region_definer(win_pos.left - 20, win_pos.top - 20)), path=path)
                # sleep(0.5)
                logger.info(f'{window_name} maximized')
            except:
                logger.warning('Window already maximized')
        return
    except Exception as error:
        logger.error('Volpe - open_window {error}')
        raise error


def volpe_back_to_main(question=False):
    '''
    Try to close all windows inside Volpe instance, reseting the UI at the end
    '''
    for _ in range(5):
        try:
            volpe_window = win_handler.activate_window('Volpe ')
        except Exception as error:
            logger.error(f'volpe_back_to_main {error}')
            raise error
        sleep(0.3)
        active_window = win32gui.GetForegroundWindow()
        active_win_text = win32gui.GetWindowText(active_window)
        sleep(0.5)
        control = win32gui.FindWindowEx(active_window, None, None, None)
        control_text = ''
        if control:
            control_text = win32gui.GetWindowText(control)
        win_pos = volpe_window.box
        pyautogui.failSafeCheck()
        if 'AVISO' in active_win_text:
            logger.debug('Space pressed')
            pyautogui.press('space')
        elif 'Save As' in active_win_text:
            pyautogui.press('esc')
        elif 'Confirmar Salvar como' in active_win_text:
            if question == False:
                pyautogui.press('n')
                logger.debug('Fale save canceled')
            else:
                pyautogui.press('s')
                logger.debug('File overwritten')
            pyautogui.press('esc')
        elif 'Volpe' in active_win_text:
            logger.debug('Volpe Main Window')
            try:
                pyautogui.press('esc')
                sleep(0.3)
                for _ in range(5):
                    win_handler.icon_click('Volpe_Close_Inactive.png', confidence_value=0.9, region_value=(region_definer(win_pos.left, 
                                    win_pos.top + 15, 
                                    width=win_pos.width + 20, 
                                    height=win_pos.height + 20)))
                logger.info('Close')
            except Exception as error:
                logger.warning(f'Close button not found due {error}')
        else:
            if control_text == '&Sim':
                pyautogui.press('n')
            else:
                pyautogui.press('esc')
    pyautogui.hotkey('ctrl', 'e')
    pyautogui.failSafeCheck()
    sleep(2)
    return


def volpe_load_report(start_date=datetime.datetime, 
            date_end=datetime.datetime,
            tab_name=str,
            confirm_button=str,
            date_from_image=str,
            date_until_image=str,
            report_load_wait=str,
            date_from_pos='Front',
            date_from_dist=25,
            date_until_pos='Front',
            date_until_dist=25,
            reference_pos_image=None,
            load_report_path='Images'):
    '''
    Volpe automation to load report by date
    '''
    try:
        if not tab_name == None:
            volpe_tab_select(tab_name, path=load_report_path)
        if not reference_pos_image == None:
            reference_pos = win_handler.image_search(reference_pos_image, path=load_report_path, confidence_value=0.95)
        else:
            reference_pos = win_handler.get_window_size()
        date_from = win_handler.image_search(date_from_image, 
                            path=load_report_path, 
                            confidence_value=0.95,
                            region=(region_definer(reference_pos.left - 15, reference_pos.top - 15)) if not reference_pos == None else '')
        win_handler.click_field(date_from, date_from_pos, distance=date_from_dist)
        sleep(0.3)
        pyautogui.click()
        sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        sleep(0.5)
        pyautogui.write(datetime.datetime.strftime(start_date, '%d%m%Y'))
        sleep(0.5)
        date_until = win_handler.image_search(date_until_image, 
                            path=load_report_path, 
                            confidence_value=0.95, region=(region_definer(reference_pos.left - 15, reference_pos.top - 15) if reference_pos else ''))
        win_handler.click_field(date_until, date_until_pos, distance=date_until_dist)
        sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        sleep(0.3)
        pyautogui.write(datetime.datetime.strftime(date_end, '%d%m%Y'))
        sleep(0.5)
        win_handler.icon_click(confirm_button, path=load_report_path)
        sleep(0.3)
        win_handler.loading_wait(report_load_wait, path=load_report_path)
        sleep(1)
        return
    except Exception as image_search_error:
        logger.error(f'{image_search_error}')
        raise Exception(f'load_report error {image_search_error}')


def volpe_save_report(file_name, save_path, reference=None, load_report_path='Images'):
    '''
    Volpe automation
    Save values to txt file with name and path arguments
    '''
    pyautogui.moveTo(10, 10)
    if not reference == None:
        reference_pos = win_handler.image_search(reference, path=load_report_path, confidence_value=0.8)
    else:
        reference_pos = win_handler.get_window_size()
    win_handler.icon_click('Icon_save.png', region_value=(region_definer(reference_pos.left - 15, reference_pos.top - 15) if reference_pos else ''))
    sleep(0.5)
    for _ in range(5):
        keyboard.press_and_release('down')
        sleep(0.3)
    pyautogui.press('enter')
    sleep(1)
    logger.debug('Save window')
    save_as_window = win_handler.image_search('Title_Save_as.png')
    if save_as_window:
        file_full_path = join(os.path.normpath(save_path), file_name)
        file_handler.check_create_dir(save_path)
        pyautogui.write(file_full_path)
        sleep(0.5)
        pyautogui.press(['tab', 'tab'])
        sleep(0.5)
        pyautogui.press('enter')
        sleep(1.0)
        logger.debug(f'File {file_name} saved')
        message_box_confirm()
        sleep(0.5)
    return


def message_box_confirm(check_count: int=5, override: bool=True):
    '''
    Volpe messagebox and warning treat
    '''
    for _ in range(check_count):
        try:
            active_window = win32gui.GetForegroundWindow()
            win_title = win32gui.GetWindowText(active_window)
            control = win32gui.FindWindowEx(active_window, None, None, None)
            control_text = ''
            logger.debug(f'Title {win_title}')
            if control:
                control_text = win32gui.GetWindowText(control)
            if 'Volpe' in win_title:
                logger.debug('"Volpe" return')
                return
            elif 'AVISO' in win_title:
                logger.debug('"AVISO" Space pressed')
                pyautogui.press('space')
                sleep(0.3)
            elif 'Save As' in win_title:
                logger.debug('"Save As" Esc pressed')
                pyautogui.press('esc')
                sleep(0.3)
            elif 'Confirmar Salvar como' in win_title:
                if override == True:
                    logger.debug('"Confirmar Salvar como" File overwritten')
                    pyautogui.press('s')
                else:
                    logger.debug('"Confirmar Salvar como" File save cancel')
                    pyautogui.press('n')

                sleep(0.3)
            else:
                if '&Sim' in control_text:
                    logger.debug('"Open file" N pressed')
                    pyautogui.press('n')
                else:
                    logger.debug('"Open file" Esc pressed')
                    pyautogui.press('esc')
                sleep(0.3)
            win_handler.activate_window('Volpe ')
            sleep(1.5)
        except Exception as error:
            logger.error(f'Message box confirm error due {error}')
    return


def load_product_code(code=str, field_pos='Bellow', distance=15, field_name=str, consult_button=str, path=str):
    '''
    Load values using product code in specific Volpe window
    '''
    try:
        product_pos = win_handler.image_search(field_name, path=path)
        sleep(0.3)
        win_handler.click_field(product_pos, field_pos, distance)
        sleep(0.6)
        pyautogui.click()
        sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        sleep(0.5)
        pyautogui.write(code)
        sleep(0.3)
        win_handler.icon_click(consult_button, path=path)
        return
    except Exception as error:
        logger.error(f'Load product code error {error}')
        raise Exception(f'Load product code {error}')


def type_selector(window_name, reference_field: str, reference_field_pos: str, tab_times: int, path, *args) -> None:
    '''
    Select production type, will be moved to erp_volpe_hadler
    This function should be compatible with any Sell Type Selection in VOLPE ERP
    '''
    try:
        win_pos = win_handler.image_search(window_name, path=path)
        sleep(0.5)
        reference_pos = win_handler.image_search(reference_field, path=path)
        win_handler.click_field(reference_pos, reference_field_pos)
        sleep(0.7)
        for _ in range(tab_times):
            pyautogui.press('tab')
            sleep(0.4)
        pyautogui.press('space')
        sleep(0.5)
        selec_type_win_pos = win_handler.image_search('title_select_type.png', path=path)
        win_handler.icon_click('discard_all_button.png', path=path)
        discard_pos = win_handler.image_search('discard.png', path=path)
        win_handler.click_field(discard_pos, 'Bellow')
        occult_inactive = win_handler.image_search('Occult_inactive.png', path=path)
        # win_handler.click_field(occult_inactive, 'Bellow', distance=0)
        pos_x = discard_pos.left + 30
        pos_y = discard_pos.top + discard_pos.height + 5
        fields_list = []
        while not len(fields_list) == len(args):
            value = ctrl_d(pos_x, pos_y)
            sleep(0.5)
            if value in args:
                logger.info('Match')
                fields_list.append(value)
                pyautogui.press('enter')
                sleep(0.2)
            else:
                keyboard.press_and_release('down')
                pos_y = pos_y + discard_pos.height + 3 if pos_y + discard_pos.height + 3 < occult_inactive.top - 10 else pos_y
                sleep(0.2)
        sleep(0.5)
        win_handler.icon_click('Select_button.png', path=path)
        logger.info('Type selector done')
        return
    except Exception as error:
        logger.error(f'Error selecting type {error}')
        raise error


def delete_from_table(column_pos=pyscreeze.Box, delete_value=str, deactivate_middle_search=True) -> None:
    try:
        pyautogui.rightClick(column_pos.left + 10, column_pos.top + 5)
        sleep(0.3)
        pyautogui.write(delete_value)
        sleep(0.3)
        logger.debug(f'{delete_value} deleted')
        if deactivate_middle_search:
            for _ in range(3):
                keyboard.press_and_release('tab')
                sleep(0.3)
            keyboard.press_and_release('space')
            sleep(0.3)
            for _ in range(2):
                keyboard.press_and_release('shift + tab')
                sleep(0.3)
            keyboard.press_and_release('space')
        else:
            for _ in range(2):
                keyboard.press_and_release('enter')
                sleep(0.3)
        sleep(0.3)
        keyboard.press_and_release('delete')
        sleep(0.7)
        win_title = win_handler.get_active_windows_title()
        sleep(0.5)
        if 'DELETAR' in win_title:
            pyautogui.press('s')
            sleep(0.5)
            return
        if 'AVISO' in win_title:
            logger.warning(f'Could not find {delete_value} value.')
            keyboard.press_and_release('space')
            sleep(0.5)
            return
        else:
            raise Exception(f'Error in {delete_value} exclusion')
    except Exception as error:
        logger.error(f'Error deleting code due {error}')
        raise error


if __name__ == '__main__':
    logger = logging.getLogger()
    log_builder.logger_setup(logger)
    
    win_handler.activate_window('Volpe ')
    sleep(1.5)

    active_window = win32gui.GetForegroundWindow()
    win_title = win32gui.GetWindowText(active_window)
    control = win32gui.FindWindowEx(win_title, None, None, None)
    control_text = ''
    logger.debug(f'Title {win_title}')