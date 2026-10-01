import logging
from datetime import datetime


logger = logging.getLogger('upgrade')


class Customer:
    '''
    Customer
    --------

    Customer code and start date and end date

    Args:
        - customer_code
        - start_date
        - end_date
    '''
    def __init__(self, customer_code: int, start_date: datetime, end_date: datetime):
        self.customer_code = customer_code
        self.start_date = start_date
        self.end_date = end_date
    
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
            customer_code = int(dict_values.get('customer_code'))
            start_date = datetime.strptime('%d/%m/%Y %H%M%s', dict_values.get('start_date'))
            end_date = datetime.strptime('%d/%m/%Y %H%M%s', dict_values.get('end_date'))
            return cls(customer_code, start_date, end_date)
        except Exception as error:
            logger.error(f'Error in {error}')


class Upgrade:
    def __init__(self):
        pass



class Upgrade:
    '''
    Upgrade
    -------

    Volpe product upgrade destails

    Args
        - upgrade_name
        - upgrade_message
        - customer_list
        - original_bonus
        - require_voucher
        - start_date
        - end_date
    '''
    def __init__(self, upgrade_name: str, upgrade_message: str, customer_list: list[Customer], original_bonus: bool, require_voucher: bool, start_date: datetime.date, end_date: datetime.date):
        self.upgrade_name = upgrade_name
        self.upgrade_message = upgrade_message
        self.customer_list = customer_list
        self.original_bonus = original_bonus
        self.require_voucher = require_voucher
        self.start_date = start_date
        self.end_date = end_date

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
            upgrade_name = dict_values.get('upgrade_name')
            upgrade_message = dict_values.get('upgrade_message')
            customer_list = [Customer.init_dict(customer_id) for customer_id in dict_values.get('customer_list')]
            original_bonus = eval(dict_values.get('original_bonus'))
            require_voucher = eval(dict_values.get('require_voucher'))
            start_date = datetime.strptime('%Y/%m/%d %H:%M:%s', dict_values.get('start_date'))
            end_date = datetime.strptime('%Y/%m/%d %H:%M:%s', dict_values.get('end_date'))
            return cls(upgrade_name, upgrade_message, customer_list, original_bonus, require_voucher, start_date, end_date)
        except Exception as error:
            logger.error(f'Error in {error}')


class UpgradeList:
    '''
    UpgradeList
    -----------

    List of upgrades

    Args:
        - upgrade_list
    '''

    def __init__(self, upgrade_list: list[Upgrade]):
        self.upgrade_list = upgrade_list
    
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
            upgrade_list = [Upgrade.init_dict(upgrade) for upgrade in dict_values.get('upgrade')]
            return cls(upgrade_list)
        except Exception as error:
            logger.error(f'Error in {error}')


class UpgradeUnit:
    def __init__(self, customer_id: int, customer_name: str, upgrade_id: int, upgrade_description: str):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.upgrade_id = upgrade_id
        self.upgrade_description = upgrade_description

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
            customer_id = int(dict_values.get('customer_id'))
            customer_name = dict_values.get('customer_name')
            upgrade_id = dict_values.get('upgrade_id')
            upgrade_description = dict_values.get('upgrade_description')
            return cls(customer_id, customer_name, upgrade_id, upgrade_description)
        except Exception as error:
            logger.error(f'Error in {error}')