import zipfile
import os
import image
import configuration
from loguru import logger
from tempfile import TemporaryDirectory


def check_integrity(directory_name):
    """
    Check if the directory contains metadata.json, params.json and a Docker image tar file
    :param directory_name: the directory to check
    :return: boolean
    """
    try:
        files = os.listdir(directory_name)
    except FileNotFoundError:
        return False
    except NotADirectoryError:
        return False
    except PermissionError:
        return False
    if 'metadata.json' not in files:
        return False
    if 'params.json' not in files:
        return False
    if image.find_tarfile('.') is None:
        return False
    if not image.is_docker_image_tar(image.find_tarfile('.')):
        return False
    return True


def pack(directory_name):
    """
    Pack a directory as a cpm file
    :param directory_name: the directory to pack
    :return: none
    """
    try:
        with zipfile.ZipFile(f'{directory_name}.cpm', 'w') as f:
            for root, dirs, files in os.walk(directory_name):
                for file in files:
                    f.write(os.path.join(root, file))
    except zipfile.BadZipFile:
        logger.error(f'Failed to pack {directory_name} as a cpm file')
        return


def unpack(cpm_file):
    """
    Unpack a cpm file to current work directory
    :param cpm_file: the cpm file to unpack
    :return: none
    """
    try:
        with zipfile.ZipFile(cpm_file, 'r') as f:
            f.extractall()
    except zipfile.BadZipFile:
        logger.error(f'Failed to unpack {cpm_file}')
        return
    logger.info(f'Unpack {cpm_file} successfully')


# 从cpm文件中提取出metadata内容，保存到临时目录中，再使用configuration.Metadata类进行读取
def extract_metadata_from_cpm_file(cpm_file):
    """
    Extract metadata from a cpm file
    :param cpm_file: cpm file path
    :return: metadata dict
    """
    try:
        with TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(cpm_file, 'r') as f:
                f.extract(f'{cpm_file[:-4]}/metadata.json', path=temp_dir)
            return configuration.Metadata(os.path.join(temp_dir, f'{cpm_file[:-4]}/metadata.json')).data
    except Exception as e:
        logger.error(f'Failed to extract metadata from {cpm_file}, error: {e}')
        return None
