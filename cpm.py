"""
command:
create_template <name> : create a new template directory in current work directory
pack <name> : pack current work directory as a cpm file
unpack <name> : unpack a cpm file to current work directory
check_metadata <name> : check the format of a metadata.json file
check_params <name> : check the format of a params.json file
check_params_consistency <name> : check the consistency of params.json file and docker image file
info <name> : print the metadata and params file
"""
import os
import json
from pprint import pprint
from templates import *
import utils, image, configuration
import fire
from loguru import logger


class Command:
    def create_template(self, cpm_directory_name):
        """
        Create a new template directory in current work directory
        :param cpm_directory_name:
        :return:
        """
        try:
            os.mkdir(cpm_directory_name)
        except FileExistsError:
            logger.error(f'Folder {cpm_directory_name} already exists, please delete it first')
            return
        with open(os.path.join(cpm_directory_name, 'metadata.json'), 'w') as f:
            metadata = json.dumps(METADATA_JSON_TEMPLATE, indent=4, ensure_ascii=False)
            f.write(METADATA_INSTRUCTIONS + metadata)
        with open(os.path.join(cpm_directory_name, 'params.json'), 'w') as f:
            params = json.dumps(PARAMS_JSON_TEMPLATE, indent=4, ensure_ascii=False)
            f.write(PARAMS_INSTRUCTIONS + params)
        logger.info(f'Create template {cpm_directory_name} successfully')

    def pack(self, cpm_directory_name):
        """
        Pack a directory as a cpm file to work directory
        :param cpm_directory_name:
        :return:
        """
        if not utils.check_integrity(cpm_directory_name):
            logger.error(f'Folder {cpm_directory_name} is not a valid CPM folder')
            return
        try:
            configuration.Metadata(os.path.join(cpm_directory_name, 'metadata.json')).validate()
            logger.info(f'File metadata.json in {cpm_directory_name} is valid')
        except ValueError as e:
            logger.error(f'File metadata.json in {cpm_directory_name} is not valid, {e}')
            return
        try:
            configuration.Parameters(os.path.join(cpm_directory_name, 'params.json')).validate()
            logger.info(f'File params.json in {cpm_directory_name} is valid')
        except ValueError as e:
            logger.error(f'File params.json in {cpm_directory_name} is not valid, {e}')
            return
        try:
            configuration.Parameters(os.path.join(cpm_directory_name, 'params.json')).consistency_check(
                image.find_tarfile(cpm_directory_name))
            logger.info(f'File params.json in {cpm_directory_name} is consistent with the docker image file')
        except ValueError as e:
            logger.error(f'File params.json in {cpm_directory_name} is not consistent with the docker image file, {e}')
            return
        logger.info('Passed all checks, start packing, this may take a while...')
        utils.pack(cpm_directory_name)
        logger.info(f'Pack {cpm_directory_name} as a cpm file successfully')

    def unpack(self, cpm_file):
        """
        Unpack a cpm file to current work directory
        :param cpm_file:
        :return:
        """
        utils.unpack(cpm_file)
        if not utils.check_integrity(cpm_file[:-4]):
            logger.error(f'Folder {cpm_file[:-4]} is not a valid CPM folder')
            return

    def check_metadata(self, metadata_file):
        """
        Check the format of a metadata.json file
        :param metadata_file:
        :return:
        """
        try:
            configuration.Metadata(metadata_file).validate()
            logger.info(f'File {metadata_file} is valid')
        except ValueError:
            logger.error(f'File {metadata_file} is not valid')
            return

    def check_params(self, params_file):
        """
        Check the format of a params.json file
        :param params_file:
        :return:
        """
        try:
            configuration.Parameters(params_file).validate()
            logger.info(f'File {params_file} is valid')
        except ValueError:
            logger.error(f'File {params_file} is not valid')
            return

    def check_params_consistency(self, cpm_directory_name):
        """
        Check the consistency of params.json file and docker image file
        :param cpm_directory_name:
        :return:
        """
        try:
            configuration.Parameters(os.path.join(cpm_directory_name, 'params.json')).consistency_check(
                image.find_tarfile(cpm_directory_name))
            logger.info(f'File params.json in {cpm_directory_name} is consistent with the docker image file')
        except ValueError:
            logger.error(f'File params.json in {cpm_directory_name} is not consistent with the docker image file')
            return

    def info(self, cpm_file):
        """
        Pretty print the metadata of a cpm file
        :param cpm_file:
        :return:
        """
        pprint(utils.extract_metadata_from_cpm_file(cpm_file))


if __name__ == '__main__':
    import multiprocessing

    multiprocessing.freeze_support()
    fire.Fire(Command)
