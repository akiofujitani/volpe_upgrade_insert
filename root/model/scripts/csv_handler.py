import csv, os, shutil, datetime, chardet, logging, sys
from .file_handler import file_list
from ntpath import join, abspath

logger = logging.getLogger('csv_handler')


def csv_to_list(filePath: str, delimeter_char: str='\t', case_upper: bool=True, quoting: csv.Dialect=csv.QUOTE_NONE) -> list:
    '''
    csv_to_list
    -----------

    Get csv file, read and convert it to list of dictionaries
    '''
    file_path = os.path.normpath(os.path.abspath(filePath))
    try:
        logger.debug(f'Trying to read {file_path}')
        csv_contents = __csv_reader(file_path, delimeter_char, case_upper, quoting)
    except Exception as error:
        logger.warning(f'Read error {error}')
        try:
            try:
                logger.debug('Trying to read csv file on default enconde ISO-8859-1')
                csv_contents = __csv_reader(filePath, delimeter_char, case_upper,  encoding='ISO-8859-1')
            except:
                logger.debug('Find best suited enconde and try to read')
                encoding = __detect_encode(filePath)
                csv_contents = __csv_reader(filePath, delimeter_char, case_upper, encoding=encoding)
        except:
            raise Exception('Could not read file contents')        
    return csv_contents


def __csv_reader(file_path: str,  delimeter_char: str, case_upper: bool=True, quoting: csv.Dialect=csv.QUOTE_NONE, encoding: str='utf-8'):
    '''
    csv_reader
    ----------

    Auxiliary method for CSVtoList
    '''
    with open(file_path, encoding=encoding) as csv_file:
        try:
            csv_reader = csv.reader(csv_file, delimiter=delimeter_char, quoting=quoting)
            header = []
            header = next(csv_reader)

            csv_contents = []
            for row in csv_reader:
                row_Contents = {}
                for key in range(len(header)):
                    if case_upper:
                        header_value = header[key].upper()
                    else:
                        header_value = header[key]
                    row_Contents[header_value] = row[key]        
                csv_contents.append(row_Contents)
        except Exception as error:
            logger.warning(f'Could not add due {error}')
            raise error
    logger.info('CSV contents extracted')
    return csv_contents


def __detect_encode(file_path: str):
    '''
    Auxiliary method for CSVoList
    Try to detect the encoding type
    '''
    logger.debug('Try to find best suited encode for data')
    with open(file_path, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(200000))
    return result['encoding']


def listToCSV(valuesList: dict[str, str], filePath: str) -> None:
    '''
    listToCSV
    ---------

    Convert list to CSV using first line as header
    '''
    with open(filePath, 'w', newline='') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=list(valuesList[0].keys()), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(valuesList)
        logger.debug('List to CSV complete')
    return


def append_to_csv(csv_path: str, file_name: str, extension: str, items_list: list[any], headers: dict[str, str], delimiter: str='\t', quoting: csv.Dialect=csv.QUOTE_NONE) -> None:
    csv_file_list = file_list(csv_path, extension)
    if len(csv_file_list) == 0:
        with open(join(csv_path, file_name), 'w', encoding='utf-8', newline='') as write_file:
            csv_writer = csv.writer(write_file, delimiter=delimiter, quoting=quoting)
            csv_writer.writerow(headers.values())
    with open(join(csv_path, file_name), 'a', encoding='utf-8', newline='') as write_file:
        csv_writer = csv.writer(write_file, delimiter=delimiter, quoting=quoting)
        csv_writer.writerow(items_list)
    return
