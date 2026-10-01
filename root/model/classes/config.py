import logging
from os.path import normpath, abspath


logger = logging.getLogger('classes')


class Configuration:
    '''
    Configuration
    -------------

    Args
        - csv_upgrade_list: CSV_path
        - csv_upgrade_customer: CSV_path
        - csv_upgrade_period: CSV_path
        - no_monitor: bool
        - before_start_time = int
    '''
    def __init__(self, csv_upgrade_list: str, csv_upgrade_customer: str, csv_upgrade_period: str, no_monitor: bool, before_start_time: int) -> None:
        self.csv_upgrade_list = csv_upgrade_list
        self.csv_upgrade_customer = csv_upgrade_customer
        self.csv_upgrade_period = csv_upgrade_period
        self.no_monitor = no_monitor
        self.before_start_time = before_start_time
        

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True
    
    @classmethod
    def init_dict(cls, dict_values=dict):
        try:
            csv_upgrade_list = CSV_Path.init_dict(dict_values.get('csv_upgrade_list'))
            csv_upgrade_customer = CSV_Path.init_dict(dict_values.get('csv_upgrade_customer'))
            csv_upgrade_period = CSV_Path.init_dict(dict_values.get('csv_upgrade_period'))
            no_monitor = eval(dict_values.get('no_monitor'))
            before_start_time = int(dict_values.get('before_start_time'))
            return cls(csv_upgrade_list, csv_upgrade_customer, csv_upgrade_period, no_monitor, before_start_time)
        except Exception as error:
            logger.error(f'Error in {error}')


class CSV_Path:
    '''
    CSV_Path
    --------

    Args:
        - csv_path
        - csv_extension
        - csv_delimiter
    '''

    def __init__(self, csv_path: str, csv_extension: str, csv_delimiter: str):
        self.csv_path = csv_path
        self.csv_extension = csv_extension
        self.csv_delimiter = csv_delimiter

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.__class__):
            return NotImplemented
        else:
            self_values = self.__dict__
            for key in self_values.keys():
                if not getattr(self, key) == getattr(__o, key):
                    return False
            return True
        
    @classmethod
    def init_dict(cls, dict_values=dict):
        try:
            csv_path = abspath(normpath(dict_values.get('csv_path')))
            csv_extension = dict_values.get('csv_extension')
            csv_delimiter = dict_values.get('csv_delimiter')
            return cls(csv_path, csv_extension, csv_delimiter)
        except Exception as error:
            logger.error(f'Error in {error}')