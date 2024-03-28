import os
import tarfile
import json


def find_tarfile(path):
    """
    Find the tar file in the directory
    :param path: the path of the directory
    :return: tar file path
    """
    files = []
    for file in os.listdir(path):
        if file.endswith('.tar'):
            files.append(file)
    if len(files) == 0:
        raise FileNotFoundError('No tar file found in the directory')
    elif len(files) > 1:
        raise FileExistsError('More than one tar file found in the directory')
    else:
        return os.path.join(path, files[0])


def is_docker_image_tar(path):
    """
    Check if a tar file is a Docker image file
    :param path: image tar file path
    :return: boolean
    """
    with tarfile.open(path, 'r') as f:
        try:
            manifest = json.load(f.extractfile('manifest.json'))
        except KeyError:
            return False
        config = manifest[0]['Config']
        layers = [layer.split('/')[0] for layer in manifest[0]['Layers']]
        if config not in f.getnames():
            return False
        for layer in layers:
            if layer not in f.getnames():
                return False
        return True


def get_env_vars(path):
    """
    Get the environment variables in the docker image tar file
    :param path: docker image tar file path
    :return: image env list
    """
    with tarfile.open(path, 'r') as f:
        config = json.load(f.extractfile('manifest.json'))[0]['Config']
        config = json.load(f.extractfile(config))
        return [env.split("=")[0] for env in config['config']['Env']]


def get_workdir(path):
    """
    Get the working directory from the manifest.json file in the docker image tar
    :param path: docker image tar file path
    :return: working directory path
    """
    with tarfile.open(path, 'r') as f:
        config = json.load(f.extractfile('manifest.json'))[0]['Config']
        config = json.load(f.extractfile(config))
        return config['config']['WorkingDir']
