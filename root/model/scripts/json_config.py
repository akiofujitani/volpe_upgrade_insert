import json, os, logging
from os.path import exists, normpath, dirname
from os import makedirs



logger = logging.getLogger('json_config')


def load_json_config(config_file=str, template_data=None) -> dict:
    '''
    load_json_config
    ----------------

    load json file and transforms it in dictionary
    the template_data  
    '''
    norm_config_file = normpath(config_file)
    if exists(norm_config_file):
        with open(norm_config_file, encoding='utf-8') as file_data:
            return json.load(file_data)
    elif template_data:
        template_data = json.loads(template_data)
        path_directory = dirname(norm_config_file)
        if not exists(path_directory):
            makedirs(path_directory)
        with open(normpath(norm_config_file), 'w') as json_file:
            json.dump(template_data, json_file, indent=4)
            return template_data
    else:
        raise Exception('File not found and no template data inserted')


def save_json_config(config_file=str, json_config=dict) -> None:
    '''
    Save JSON Config
    ----------------
    '''
    with open(config_file, 'w') as json_file:
        json.dump(json_config, json_file, indent=4)
    return
