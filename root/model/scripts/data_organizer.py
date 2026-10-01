import logging, datetime, calendar
from ntpath import join
from .file_handler import csv_to_list, fileCreationDate


logger = logging.getLogger('data_organizer')


def jobAndFileDate(filePath, fileList):
    '''
    jobAndFileDate
    --------------

    '''
    job_list = []
    for file in fileList:
        tempDict = csv_to_list(join(filePath, file))
        tempJobSet = set()
        for line in tempDict:
            tempJobSet.add(line['PEDIDO'])
        fileDate = fileCreationDate(join(filePath, file))
        job_list.append({fileDate.strftime('%d-%m-%Y') : tempJobSet})
    return job_list


def define_start_date(date_1, date_2):
    '''
    define_start_date
    -----------------

    '''
    date_diff = date_1 - date_2
    if date_diff == datetime.timedelta(days=0):
        return date_1
    start_date = date_1 - date_diff
    if start_date == date_1 or start_date == date_2:
        return start_date + datetime.timedelta(days=1)
    return start_date


def dict_values_compare(values, conditional):
    '''
    dict_values_compare
    -------------------

    '''
    if type(values) == dict:
        for key in values.keys():
            if value_compare(values[key], conditional):
                return True
    else:
        return value_compare(values, conditional)


# Make more generic
def filter_tag_by_values(data_list, tag_conditionals):
    '''
    filter_tag_by_values
    --------------------

    '''
    filtered_values = []
    for data in data_list:
        for conditional in tag_conditionals:
            if conditional['Tag'] in data and dict_values_compare(data[conditional['Tag']], conditional):
                filtered_values.append(data)
    return filtered_values


def value_compare(value, conditional):
    '''
    value_compare
    -------------

    '''
    value = value_type_definer(value)
    if not value == '':
        match conditional['Operator']:
            case '<':
                if value < conditional['Value']:
                    return True
            case '>':
                if value > conditional['Value']:
                    return True
            case '<=':
                if value <= conditional['Value']:
                    return True
            case '>=':
                if value >= conditional['Value']:
                    return True
            case '=':
                if value == conditional['Value']:
                    return True
            case 'contains':
                if conditional['Value'] in value:
                    return True
    return False


def value_type_definer(value):
    '''
    value_type_definer
    ------------------

    '''
    if '.' in value:
        try:
            value = float(value)
        except:
            logger.debug(f'{value} is not float')
        return value
    try:
        return int(value)
    except ValueError:
        return value


def filter_by_values(data_list: list, field_name: str, *args) -> list:
    '''
    filter_by_values
    ----------------

    Filter list dictionary by values in field name
    Ex: return values with field_name = "NAME" with values ["Jonh", "Michael", "Rachel"]
    '''
    filtered_list = []
    for data in data_list:
        if data[field_name] in args:
            filtered_list.append(data)
    return filtered_list


def num_to_col_letters(num):
    '''
    num_to_col_letters
    ------------------

    '''
    letters = ''
    while num:
        mod = (num - 1) % 26
        letters += chr(mod + 65)
        num = (num - 1) // 26
    return ''.join(reversed(letters))


def convert_to_date(data_dict=list, date_format=str, date_format_out=str, *args):
    '''
    convert_to_date
    ---------------

    '''
    updated_data_dict = []
    for data in data_dict:
        temp_data = {}
        for field in data.keys():
            if field in args:
                temp_data[field] = datetime.datetime.strptime(data[field], date_format).strftime(date_format_out)
            else:
                temp_data[field] = data[field]
        updated_data_dict.append(temp_data)
    return updated_data_dict


def remove_from_dict(values_dict=dict, *args):
    '''
    remove_from_dict
    ----------------
    '''
    updated_dict = []
    for value in values_dict:
        for arg in args:
            value.pop(arg.upper())
        updated_dict.append(value)
    return updated_dict


def add_months_to_date(date: datetime.datetime, num_of_months: int) -> datetime.datetime:
    '''
    add_month_to_date
    -----------------

    '''
    for i in range(num_of_months):
        date = date + datetime.timedelta(days=calendar.monthrange(date.year, date.month)[1])
    return date


def find_duplicates(ocurrences_list=list) -> list:
    '''
    find_duplicates
    ---------------

    '''
    duplicates = []
    seen = []
    for item in ocurrences_list:
        if item in seen:
            duplicates.append(item)
        else:
            seen.append(item)
    return duplicates


def data_type_selector(data_type: str) -> object:
    '''
    data_type_selector
    ------------------

    '''
    match data_type:
        case 'float':
            return float
        case 'int':
            return int
        case 'bool':
            return bool
        case _:
            return str