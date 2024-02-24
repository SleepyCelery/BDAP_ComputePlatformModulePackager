import os
import tarfile
import json


def find_tarfile(path):
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


# 判断一个tar文件是否为Docker镜像文件，首先查看里面是否有manifest.json文件，如果有，则读取该文件里记录的配置文件和所有layer目录，并查看tar目录内是否有这些路径，如果有，则认为是Docker镜像文件
def is_docker_image_tar(path):
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


# 获取Docker镜像内的环境变量名列表
def get_env_vars(path):
    with tarfile.open(path, 'r') as f:
        config = json.load(f.extractfile('manifest.json'))[0]['Config']
        config = json.load(f.extractfile(config))
        return [env.split("=")[0] for env in config['config']['Env']]


# 获取Docker镜像内的工作目录
def get_workdir(path):
    with tarfile.open(path, 'r') as f:
        config = json.load(f.extractfile('manifest.json'))[0]['Config']
        config = json.load(f.extractfile(config))
        return config['config']['WorkingDir']

