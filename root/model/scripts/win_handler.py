import subprocess, pyscreeze, pyautogui, screeninfo, os, logging, concurrent.futures
# from . import constants
from tkinter import Tk
from ntpath import join
from time import sleep
from win32 import win32gui
from .file_handler import resource_path


executor = concurrent.futures.ThreadPoolExecutor()

logger = logging.getLogger('win_handler')


'''
==================================================================================================================================

        Classes     Classes     Classes     Classes     Classes     Classes     Classes     Classes     Classes     Classes     

==================================================================================================================================
'''


class BaseException(Exception):
    pass


class ImageNotFoundException(BaseException):
    pass


def select_get_text(pos_x: int | None=None, pos_y: int | None=None) -> str:
    '''
    Select text on given position copy it to clipboard and transforms it into string variable
    '''
    if pos_x and pos_y:
        pyautogui.move(pos_x, pos_y)
        sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    sleep(0.3)
    clipboard_value = Tk().clipboard_get()
    logger.info(f'Clipboard value {clipboard_value}')
    return clipboard_value


def activate_window(window_name: str):
    '''
    Finds a window by name a activates it
    If multiples windows with the same name, activates the last active one.
    '''
    try:
        window_name_list = pyautogui.getWindowsWithTitle(window_name)
        # win32gui.SetForegroundWindow(window_name_list[0]._hWnd)
        # sleep(0.5)
        if not window_name_list[0].isMaximized or window_name_list[0].isMinimized:
            window_name_list[0].maximize()
        if not window_name_list[0].isActive:
            window_name_list[0].activate()
        sleep(2)
        # win32gui.SetActiveWindow(window_name_list[0]._hWnd)
        pyautogui.click(window_name_list[0].center.x, window_name_list[0].box.top + 5)
        return window_name_list[0]
    except Exception as error:
        logger.error(f'Activate window: {window_name} do not exists due {error}')
        raise error


def get_window_size():
    '''
    retrieves the size of the active window
    '''
    win = pyautogui.getActiveWindow()
    return win.box


def translate_pos(pos_value, mon_pos_list, direction): 
    start= 0
    try:
        for i in range(len(mon_pos_list)):
            if pos_value >= mon_pos_list[i][direction] and pos_value <= mon_pos_list[i][direction] + mon_pos_list[i]['width' if direction == 'x' else 'height']:
                if pos_value < 0:
                    trans_pos = start + abs(mon_pos_list[i][direction]) + pos_value
                else:
                    trans_pos = start + pos_value
                logger.debug(trans_pos)
                return trans_pos
            start = start + abs(mon_pos_list[i][direction] + mon_pos_list[i + 1][direction])
    except IndexError:
        if pos_value < mon_pos_list[0][direction]:
            return 0
        else:
            return start + mon_pos_list[i]['width' if direction == 'x' else 'height']


def get_monitors():
    monitors = screeninfo.get_monitors()
    mon_pos_x = []
    mon_pos_y = []

    for monitor in monitors:
        mon_pos_x.append({'x' : monitor.x, 'width' : monitor.width})
        mon_pos_y.append({'y' : monitor.y, 'height' : monitor.height})

    mon_pos_x= sorted(mon_pos_x, key=lambda value: value['x'])
    mon_pos_y= sorted(mon_pos_y, key=lambda value: value['y'])
    mon_pos = {'x' : mon_pos_x, 'y' : mon_pos_y}
    logger.debug(f'{mon_pos["x"]} x {mon_pos["y"]}')
    return mon_pos


def translate_xy_pos(position_x, position_y):
    mon_pos = get_monitors()
    x_pos = translate_pos(position_x, mon_pos['x'], 'x')
    y_pos = translate_pos(position_y, mon_pos['y'], 'y')
    logger.debug(f'{x_pos} x {y_pos}')
    return pyautogui.Point(x_pos, y_pos)


def image_path_fix(path=str):
    path = resource_path(path)
    if path.endswith('/'):
        return path
    if path.endswith('\\') or '\\' in path:
        return path.replace('\\', '/')
    else:
        return f'{path}/'


def locate_image(image_path: str, confidence: float, region: tuple, minSearchTime=1, *args, **kwargs):
    try:
        image_pos = pyautogui.locateOnScreen(image_path, minSearchTime=minSearchTime, confidence=confidence, region=region, *args, **kwargs)
        return image_pos
    except ImageNotFoundException as excep:
        logger.warning(f'locate_image error {excep}')
        raise None


def image_search(image_name=str, confidence_value=0.7, region=None, path='images/') -> pyscreeze.Box:
    '''
    Search image base on its name and path
    uses the confidence values starting at... going down through each pass.

    Need to find a way to insert or not the position to search in the screen
    '''
    image_path = resource_path(os.path.normpath(f'{image_path_fix(path)}/{image_name}'))
    try:
        image_pos= locate_image(image_path, confidence_value, region)
        # threading_value = executor.submit(locate_image, image_path, confidence_value, region, 0.5)
        # image_pos = threading_value.result()
        # for _ in range(3):
        #     image_pos = pyautogui.locateOnScreen(image_path, minSearchTime=0.5, confidence=confidence_value, region=region)
        if not image_pos == None:
            logger.debug(f'{image_name} found at {image_pos.left} x {image_pos.top}')
            return image_pos
        else:
            raise ImageNotFoundException
            # if i == num_tries - 1:
            #     raise ImageNotFoundException
            # confidence_value = confidence_value - 0.05
            # print(f'Seaching {image_name} Confidence value: {confidence_value}')
    except OSError as error:
        raise Exception(f'OSError: {error} {image_name}')
    except ImageNotFoundException:
        error_string = f'ImageNotFound: {image_name}'
        raise Exception(error_string)
    except Exception as error:
        raise Exception(f'Image_search exception {error}')
    except KeyboardInterrupt as error:
        raise error


def icon_click(icon_name=str, confidence_value=0.8, region_value=None, path='images/'):
    '''
    Normal Icon click
    Finds the icon image and click in its center    
    '''
    try:
        cursor_pos = pyautogui.position()
        sleep(0.3)
        icon_pos = image_search(icon_name, confidence_value=confidence_value, region=region_value, path=path)
        sleep(0.5)
        click_volpe(icon_pos)
        pyautogui.moveTo(cursor_pos.x, cursor_pos.y)
        pyautogui.failSafeCheck()
        return
    except Exception as error:
        logger.error(f'Could not find {icon_name} icon')
        raise error
    except KeyboardInterrupt as error:
        raise error


def tab_select(tab_name=str, confidence_value=0.9999999, confidence_reduction_step=0.0000003):
    '''
    tab searck and selection
    confidence values are still not completed tested
    works with a few tries with high confidenve value to acheive the mininum of false positives    
    '''
    cursor_pos = pyautogui.position()
    tabs = ['active', 'inactive']
    try:
        for _ in range(4):
            pyautogui.failSafeCheck()
            for tab_status in tabs:
                try:
                    tab_pos = image_search(f'{tab_name}_{tab_status}.png', confidence_value)
                    if tab_status == 'inactive':
                        tab_center = pyautogui.center(tab_pos)
                        click_volpe(tab_center)
                        pyautogui.moveTo(cursor_pos.x, cursor_pos.y)
                    sleep(0.5)
                    return
                except Exception as error:
                    logger.error(f'{tab_status} not found at {confidence_value}')
            confidence_value = confidence_value - confidence_reduction_step
    except Exception as error:
        raise Exception(f'Tab not found due {error}')
    except KeyboardInterrupt as error:
        raise error


def run_application(path: str, app_name: str):
    '''
    Can't comment much, got this from internet.
    Just created a way to insert variables of file and path and later convert it to bytes
    '''
    try:
        cmd_line = ['cmd', '/q', '/k', 'echo off']
        cmd = subprocess.Popen(cmd_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        temp= f'\n cd {resource_path(path)}\n {app_name}\n exit\n'
        batch = bytes(temp, 'utf-8')
        cmd.stdin.write(batch)
        cmd.stdin.flush()
        result = cmd.stdout.read()
        logger.debug(result.decode())
    except Exception as error:
        raise error
    except KeyboardInterrupt as error:
        raise error
    return


def loading_wait(image_name = str, path='Images', wait_time_in_sec = 15):
    '''
    Special function to application loading.
    Image based wait
    Set the last thing that the application will load at the screen
    '''
    counter = 0
    while True:
        try:
            root_pos = image_search(image_name, confidence_value=0.9, path=path)
            if root_pos:
                return root_pos
        except Exception as error:
            logger.info(f'Not loaded {error}. Count {counter}')
            if counter >= wait_time_in_sec:
                raise Exception('Software frozen or loading too slow')
            counter = counter + 1
        except KeyboardInterrupt as error:
            raise error
        sleep(1)

def click_volpe(pos, time=0.2):
    '''
    I don't believe in this, a software need a slow click like drag to work.
    '''
    try:
        if type(pos) == pyautogui.Point:
            pos_centered = pos
        else:
            pos_centered = pyautogui.center(pos)
        pyautogui.moveTo(pos_centered.x, pos_centered.y)
        sleep(0.3)
        pyautogui.dragTo(pos_centered.x, pos_centered.y, time, button='left')
        logger.debug('click')
        pyautogui.failSafeCheck()
    except KeyboardInterrupt as error:
        raise error
    return


def click_field(field_pos=pyscreeze.Box, click_pos='Front', distance=20):
    '''
    text field title position
    click_pos = Front, Back, Bellow, Above
    distance in X from image left position
    distance in Y from image top position
    '''
    try:
        left = field_pos.left
        top = field_pos.top
        width = field_pos.width
        height = field_pos.height
        pyautogui.failSafeCheck()
        match click_pos:
            case 'Front':
                pyautogui.moveTo(left + width + distance, top + height / 2 + 6)
                logger.debug('Front')
            case 'Back':
                pyautogui.moveTo(left - distance, top + height / 2 + 6)
                logger.debug('Back')
            case 'Bellow':
                pyautogui.moveTo(left + 20, top + height + distance)
                logger.debug('Bellow')
            case 'Above':
                pyautogui.moveTo(left + 20, top - distance)
                logger.debug('Above')
        sleep(0.3)
        click_volpe(pyautogui.position())
        sleep(0.5)
        logger.info('Field has been clicked')
    except KeyboardInterrupt as error:
        raise error
    return 


def region_definer(raw_x, raw_y, width=None, height=None):
    '''
    Specic for image_search, translate position and return tuple with left, top, width and height
    '''
    try:
        windows_size = get_window_size()
        # start = translate_xy_pos(raw_x, raw_y)
        return pyscreeze.Box(raw_x, raw_y, windows_size.width if not width else width, windows_size.height if not height else height)
    except KeyboardInterrupt as error:
        raise error

def get_active_windows_title() -> str:
    '''
    Get active window title
    '''
    try:
        sleep(0.3)
        win_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        logger.info(win_title)
        return win_title
    except Exception as error:
        logger.error(f'Fail to get windows title due {error}')
        raise error
    except KeyboardInterrupt as error:
        raise error


def temp_fun(test: str):
    print(test)
    return test.upper()


if __name__ == '__main__':
    print(resource_path('/'))
    value = 'Teste'
    with concurrent.futures.ThreadPoolExecutor() as executor:
        temp_value = executor.submit(temp_fun, value)
        result = temp_value.result()
        print(result)
