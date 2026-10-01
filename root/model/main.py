import logging
from threading import Event, Thread
from .database import Database
# from .gui_config import GuiConfiguration
from .volpe_upgrade_insert import volpe_upgrade_insert as main_routine
from .white_label_unlock import white_label_unlock
from .scripts.json_config import load_json_config
from .templates import data_object_list


routine_name = 'volpe_upgrade_insert'

logger = logging.getLogger('main_model')


class Model():
    '''
    Model
    -----

    Load all data and runs the application logic
    '''
    def __init__(self) -> None:
        try:
            self.database = Database.init_dict(load_json_config('./data/data_object_list.json', data_object_list))  
            # self.gui_configuration = GuiConfiguration.init_dict(load_json_config('./data/gui_configuration.json', gui_configuration))
        except Exception as error:
            logger.error(f'Could not load data_object_list.json due {error}')
            raise(error)
        self.event = Event()
        self.thread = None        

    def start_routine(self):
        logger.info('starting routine')
        if not self.routine_active():
            self.event.clear()
            self.thread = Thread(target=main_routine, args=(self.database, self.event, ), name=routine_name)
            self.thread.start()

    def stop_routine(self):       
        if self.routine_active():
            logger.info('stopping routine')
            self.event.set()
            self.thread.join()
        return

    def restart_routine(self):
        self.stop_routine()
        self.start_routine()

    def routine_active(self):
        if not self.thread:
            logger.info('No thread created')
            return False
        if not self.thread.is_alive():
            logger.info('Thread is already stopped')
            return False
        return True  

    def on_close(self):
        if not self.thread:
            return
        if not self.thread.is_alive():
            return
        self.stop_routine()
        self.thread.join()
        logger.info('Thread termination complete')
