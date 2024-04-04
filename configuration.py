import json
import image


class BaseConfiguration:
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
    FIELDS_INCLUDED = {
        'USERFILES_DIR': str,
        'PARAMS': dict
    }
    PARAMS_TYPES = ['string', 'file', 'number', 'enum', 'boolean']

    def validate(self):
        for field, value in self.data.items():
            if field not in self.FIELDS_INCLUDED.keys():
                raise ValueError(f'Field {field} not found in params.json')
            if type(value) != self.FIELDS_INCLUDED[field]:
                raise ValueError(f'Field {field} should be {self.FIELDS_INCLUDED[field]} type')
        for param_name, (param_type, param_description) in self.data['PARAMS'].items():
            if param_type not in self.PARAMS_TYPES:
                raise ValueError(
                    f'Invalid param type {param_type} for param {param_name}, should be one of {self.PARAMS_TYPES}')

    def consistency_check(self, docker_image_tar_path):
        if not image.is_docker_image_tar(docker_image_tar_path):
            raise ValueError(f'File {docker_image_tar_path} is not a valid docker image tar file')
        env_vars = image.get_env_vars(docker_image_tar_path)
        for param_name in self.data['PARAMS'].keys():
            if param_name not in env_vars:
                raise ValueError(f'Param {param_name} not found in docker image tar file')
