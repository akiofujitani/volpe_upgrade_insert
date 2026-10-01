import logging
from enum import Enum
from datetime import datetime, time
from os.path import basename, dirname
from . import templates
from .scripts.json_config import save_json_config, load_json_config
from .scripts.file_handler import file_move_copy, fileMoveRename
from .classes.config import Configuration


logger = logging.getLogger('configuration')


class DataObject:
    '''
    DataObject
    ----------

    Args
        - file_path (str)
        - class_object (str)

    Methods
        - init_dict (classmethod)
    '''
    def __init__(self, file_path: str, class_object: str) -> None:
        self.file_path = file_path
        self.class_object = class_object

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
    def init_dict(cls, dict_values: dict) -> object:
        file_path = dict_values.get('file_path')
        class_object = dict_values.get('class_object')
        return cls(file_path, class_object)


class DataObjectList:
    '''
    DataObjectList
    --------------

    Args
        - data_object_dict

    Method
        - init_dict (classmethod)
    '''
    def __init__(self, data_object_dict: dict[str, object]) -> None:
        self.data_object_dict = data_object_dict
    
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
    def init_dict(cls, dict_values: dict) -> object:
        data_dict_object = {}
        for key, value in dict_values.items():
            data_dict_object[key] = DataObject.init_dict(value)
        return cls(data_dict_object)


class Database:
    '''
    Database
    --------

    Args
        - config_dict
        - config_path

    Method
        - get
        - save_backup
        - save_update
        - check_table_difference
        
        - to_dict (classmethod)
        - init_dict (classmethod)
    '''
    def __init__(self, config_dict: dict[str, object], config_path: dict[str, str]) -> None:
        self.config = config_dict
        self.config_path = config_path
        self.last_modify = datetime.now()    

    def get(self, object_name) -> object:
        return self.config.get(object_name)

    def save_backup(self, table_path: str) -> None:
        try:
            table_dir = dirname(table_path)
            table_name_ext = basename(table_path).split('.')
            now = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
            file_name = f'{table_name_ext[0]}_{now}.{table_name_ext[1]}'
            fileMoveRename(table_dir, table_dir, basename(table_path), file_name)
            return
        except Exception as error:
            logger.error(f'Could not save copy of {file_name} due {error}')
            raise error

    def save_update(self, table: str, value: object) -> None:
        table_path = self.config_path.get(table)
        value_dict = self.to_dict(value)
        if not load_json_config(table_path, None).__eq__(value_dict):
            self.save_backup(table_path)
            save_json_config(table_path, value_dict)
        self.last_modify = datetime.now()
        self.config[table] = value

    def check_table_difference(self, table: str, value: object) -> bool:
        table_path = self.config_path.get(table)
        value_dict = self.to_dict(value)    
        if load_json_config(table_path, None).__eq__(value_dict):
            return True
        return False

    @classmethod
    def __get_object(cls, object_name: str) -> object:
        match object_name:
            case 'Configuration':
                return Configuration


    @classmethod
    def to_dict(cls, any_value: any) -> dict[str, str]:
        '''
        Transform given value to string type
        '''
        try:
            if isinstance(any_value, dict):
                dict_values = {}            
                for key, value in any_value.items():
                    key = str(key)
                    if '__' in key:
                        key = key.split('__')[-1]
                    dict_values[key] = cls.to_dict(value)
                return dict_values
            elif isinstance(any_value, list):
                value_list = []
                for item_value in any_value:                    
                    value_list.append(cls.to_dict(item_value))                
                return value_list
            elif isinstance(any_value, str) or isinstance(any_value, int) or isinstance(any_value, float) or isinstance(any_value, bool):
                if '\\' in str(any_value):
                    any_value = any_value.replace('\\', '/')
                return str(any_value)
            elif isinstance(any_value, type):
                return any_value.__name__
            elif isinstance(any_value, Enum): 
                return str(any_value.value)
            elif isinstance(any_value, datetime):
                return datetime.strftime(any_value, '%Y/%m/%d %H:%M:%S')
            elif isinstance(any_value, time):
                return str(f'{any_value.hour:02d}:{any_value.minute:02d}:{any_value.second:02d}')
            elif any_value == None or any_value == '':
                return ''
            else: 
                return cls.to_dict(any_value.__dict__)
        except Exception as error:
            logger.error(f'{error}')
            raise error


    @classmethod
    def init_dict(cls, object_list: dict[DataObject]) -> object:
        class_dict = {}
        config_dict = {}
        for key, value in object_list.items():
            class_object = cls.__get_object(value.get('class_object'))
            json_dict = load_json_config(value.get('file_path'), getattr(templates, key))
            class_dict[key] = class_object.init_dict(json_dict)
            config_dict[key] = value.get('file_path')
            logger.info(f'{key} successfully loaded')
        return cls(class_dict, config_dict)
