import json
import image
import os
import re


class BaseConfiguration:
    """
    Base class for configuration files.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            uncleaned_data = f.readlines()
            try:
                # delete row begin with #
                self.data = json.loads(''.join([line for line in uncleaned_data if not line.startswith('#')]))
            except json.JSONDecodeError:
                raise ValueError(
                    f'File {filepath} is not a valid json file, please check the format and the data type!')

    def validate(self):
        pass


class Metadata(BaseConfiguration):
    """
    Class for metadata.json file.
    """
    FIELDS_INCLUDED = {
        'NAME': str,
        'IMAGE': str,
        'DESCRIPTION': str,
        'AUTHOR': str,
        'NEED_GPU': bool
    }

    def validate(self):
        for field, value in self.data.items():
            if field not in self.FIELDS_INCLUDED.keys():
                raise ValueError(f'Field {field} not found in metadata.json')
            if type(value) != self.FIELDS_INCLUDED[field]:
                raise ValueError(f'Field {field} should be {self.FIELDS_INCLUDED[field]} type')


class Parameters(BaseConfiguration):
    """
    Class for params.json file.
    """
    FIELDS_INCLUDED = {
        'TASKFILES_DIR': str,
        'PARAMS': dict
    }
    PARAMS_TYPES = ['string', 'file', 'number', 'enum', 'boolean']

    def validate(self):
        for field, value in self.data.items():
            if field not in self.FIELDS_INCLUDED.keys():
                raise ValueError(f'Field {field} not found in params.json')
            if type(value) != self.FIELDS_INCLUDED[field]:
                raise ValueError(f'Field {field} should be {self.FIELDS_INCLUDED[field]} type')
            if field == 'TASKFILES_DIR':
                if not os.path.isabs(value):
                    raise ValueError(f'TASKFILES_DIR {value} is not an absolute path')
                if not re.match(r'^(/[^/ ]*)+/?$', value):
                    raise ValueError(f'TASKFILES_DIR {value} is not a valid Linux path')
        for param_name, params in self.data['PARAMS'].items():
            if params[1] not in self.PARAMS_TYPES:
                raise ValueError(
                    f'Invalid param type {params[1]} for param {param_name}, should be one of {self.PARAMS_TYPES}')
            if params[1] == 'enum':
                if len(params) != 5:
                    raise ValueError(f'Length of params for enum type should be 5')
                if not isinstance(params[3], list):
                    raise ValueError(f'Param {param_name} is enum type but has no options')
            else:
                if len(params) != 4:
                    raise ValueError(f'Length of params for non-enum type should be 4')

    def consistency_check(self, docker_image_tar_path):
        if not image.is_docker_image_tar(docker_image_tar_path):
            raise ValueError(f'File {docker_image_tar_path} is not a valid docker image tar file')
        env_vars = image.get_env_vars(docker_image_tar_path)
        for param_name in self.data['PARAMS'].keys():
            if param_name not in env_vars:
                raise ValueError(f'Param {param_name} not found in docker image tar file')
