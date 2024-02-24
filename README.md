#  生物医学数据分析平台功能模块封装规约

## 1. 本地修改

### 1.1 修改程序输入输出

平台将以环境变量的方式传入程序的运行参数，故程序内应规定相关输入参数所对应的环境变量，并使用相关库读取环境变量的值，下面以Python语言为例。

```Python
# 导入os模块，Python语言中使用os模块读取和设置当前的环境变量
import os


# 定义运行算法的主函数，假设分析算法的主函数为main，需要输入的运行参数为data_path和params，其中data_path和params均为字符   串类型，data_path接收需要分析的数据的路径，params接收运行参数
def main(data_path:str, params:str) -> None：
		# 算法输入的文件路径为data_path,只能是当前工作目录的相对路径，如当前工作目录为/taskdata，data_path变量的值为input.txt，则最后程序读取文件的实际路径是/taskdata/input.txt
		with open(data_path, mode="rb") as data:
    		# 这里执行实际的分析算法
      	# 假设最后的输出结果暂存到变量result当中
    # 假设算法输出的文件为result.txt，保存到程序当前的工作目录下
    with open("result.txt", mode="w") as result_file:
      	result_file.write(result)
    # 此时结果文件result.txt写入的绝对路径为/taskdata/result.txt
    # 程序在运行过程中使用print输出关键信息，运行过程中作为标准输出，用户可以通过平台直接获取标准输出和标准错误的所有信息
    print("分析完成")


# 建议在下面的部分设置程序的工作目录以及运行的输入参数
if __name__ == "__main__":
  	# 由于用户只能对任务目录下的文件进行管理，平台会将用户的任务目录挂载到程序运行环境的某个目录下，因此需要确定这个目录的具体位置，这里假设需要平台将任务目录挂载到/taskdata。则程序需要从/taskdata目录下读取用户的输入数据，程序将分析好的结果文件同样保存到/taskdata目录下，便于用户从平台获取分析结果。为方便路径管理，可以直接将程序运行的工作目录设置为/taskdata目录，使用os.chdir()即可修改程序的当前工作目录
  	os.chdir("/taskdata")
    # 假设程序从DATA_PATH环境变量中读取到算法的data_path输入参数，这里需要注意进行强制类型转换，避免程序运行错误
  	data_path = str(os.getenv("DATA_PATH"))
    # 假设程序从PARAMS环境变量中读取到算法的params输入参数，这里需要注意进行强制类型转换，避免程序运行错误
  	params = str(os.getenv("PARAMS"))
    # 执行程序
    main(data_path, params)
    # 至此完成分析流程，输出数据保存到工作目录中当中

```

### 1.2 本地测试

对程序输入输出修改完成之后，应进行本地测试，确保修改完成的分析算法可以正常运行。对于常用的PyCharm等集成化开发环境，可以在运行参数配置界面对程序运行时的环境变量进行编辑。

![image-20240402105850850](http://124.222.6.157:19000/admin-picture/20240403010405.png)

点击编辑按钮，即可打开运行参数的配置界面。

![image-20240402105925174](http://124.222.6.157:19000/admin-picture/20240403010358.png)

修改环境变量的内容，即可修改程序运行的输入参数。

对于使用简单的文本编辑器的情况，可以直接在终端使用export命令设置当前的环境变量。如下所示：

```shell
export DATA_PATH=test.txt
export PARAMS="params"
```

然后将运行需要的数据复制到程序内设定好的工作目录下即可。确保程序在该环境下运行通过后，即可进行下一步。

### 1.3 导出程序运行依赖

以Python为例，对于使用venv管理的项目，可以直接在venv环境下使用下面的命令直接导出依赖项：

```shell
pip freeze > requirements.txt
```

对于Poetry管理的环境，可以使用下面命令导出依赖项：

```
poetry export --without-hashes -f requirements.txt --output requirements.txt
```

如果程序在开发过程中没有使用任何环境管理工具，可以将程序迁移到虚拟环境中，安装好相关依赖测试程序可以正常运行后，再进行导出依赖的操作。

## 2. 构建Docker镜像

### 2.1 编写Dockerfile

要将算法代码与相关运行环境进行打包为Docker镜像，需要编写Dockerfile，明确功能模块运行时需要的依赖项、配置和环境。以下为封装Python算法的Dockerfile例子：

```dockerfile
# 从Python3.9构建基础镜像
FROM python:3.9 
# 设置封装镜像时的工作目录
WORKDIR /src
# 将构建目录下的所有文件复制到镜像内的工作目录下
COPY . .
# 按照requirements.txt文件中的依赖项目安装依赖包，并设置好时区等基本信息，对于特别的依赖需求也可以在这里安装
RUN pip install --no-cache-dir -r requirements.txt &&\
    /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime &&\
    echo 'Asia/Shanghai' >/etc/timezone
#设置环境变量为程序默认参数
ENV DATA_PATH test.txt
ENV PARAMS params
#容器启动后执行python main.py命令
ENTRYPOINT ["python","main.py"]
```

在编辑完Dockerfile之后保存到源代码目录下，并将整个源代码目录复制到带有Docker的运行环境中，为创建镜像做好准备。

### 2.2 创建Docker镜像

使用以下命令创建Docker镜像：

```shell
docker build . -t <imagename>:<version>
```

其中，imagename是自定义的镜像名称，version是对应的版本号，在具有Dockerfile的目录下执行此命令，即可按照Dockerfile中的指令执行镜像构建流程。在构建完成后，可以通过docker images命令查看本地已有的Docker镜像文件。

### 2.3 使用Docker镜像创建容器进行测试

对已经创建好的Docker镜像镜像测试，确保其工作正常，首先创建一个测试目录，用于存放测试数据：

```shell
mkdir testdata
```

将测试数据通过文件传输工具保存到testdata目录后，使用以下命令创建Docker镜像：

```shell
docker run -v ./test_data:/taskdata -e DATA_PATH=test.txt -e PARAMS=params --name test_container <imagename>:<version>
```

其中，`-v ./test_data:/taskdata`表示将宿主机当前工作目录的test_data文件夹挂载到容器内的/taskdata目录下，`-e DATA_PATH=test.txt -e PARAMS=params`则表示设定容器运行的环境变量，对应算法实际运行时要读取的环境变量值。通过使用此镜像运行容器镜像测试，观察输出结果是否符合预期。

### 2.4 导出Docker镜像归档文件

当确定镜像通过测试后，即可将镜像导出为归档文件，使用以下命令导出：

```shell
docker save <image> -o image.tar
```

上述命令中，`<image>`表示镜像的md5值或者镜像的名称，`-o image.tar`则表示将镜像文件导出为image.tar文件并输出。执行此命令后，可以在当前工作目录下看到导出的image.tar文件。

## 3. 功能模块封装

### 3.1 下载并配置功能模块封装工具

执行以下命令，将功能模块封装工具的二进制文件下载到本地（当前仅限x86 CPU架构下的Linux环境运行）：

```shell
mkdir cpmtools
cd cpmtools
curl -L -o cpmtools_binary_linux_x86_64.zip https://github.com/SleepyCelery/BDAP_ComputePlatformModulePackager/releases/download/v0.1/binary_linux_x86_64.zip
unzip cpmtools_binary_linux_x86_64.zip -d .
sudo chmod +x cpm
```

当前目录下的cpm文件即为功能模块封装工具的二进制文件，可以使用./cpm命令查看所有可用命令，如果想要执行全局安装，可以将此二进制文件移动到/usr/local/bin目录下，即执行以下命令：

```shell
sudo mv cpm /usr/local/bin
```

即可在任意目录使用cpm命令执行操作。

### 3.2 创建功能模块模版目录

在任意目录下使用`cpm create_template <folder_name>`命令创建功能模块模板目录，可以发现在当前工作目录下有名为<folder_name>的目录生成，内部包含metadata.json与params.json两个模板文件。

### 3.3 编辑元数据文件

使用文本编辑器打开metadata.json文件，可看到类似下面的模板内容：

![image-20240403005353144](http://124.222.6.157:19000/admin-picture/20240403010350.png)

其中，NAME字段为功能模块的名称，平台通过此名称唯一识别功能模块。IMAGE字段为Docker镜像文件的标记，用于推送到平台内部的镜像仓库。DESCRIPTION字段为功能模块的详细描述，用于向用户展示功能模块的详细信息。AUTHOR字段为作者信息。NEED_GPU字段为运行此功能模块是否需要GPU，如果设置为true，则平台在使用该功能模块创建计算任务时会自动将任务调度到GPU节点上，如果设置为false，则会采用默认的调度策略（注意该字段为布尔类型，只能为true或者false）。

将上述文件进行编辑并保存即可。

### 3.4 编辑运行参数文件

使用文本编辑器打开params.json文件，可看到类似下面的模板内容：

![image-20240403010916836](http://124.222.6.157:19000/admin-picture/20240403010917.png)

其中，TASKFILES_DIR字段设置需要平台将任务数据目录挂载到容器的哪个位置，一般为算法代码中选定的工作目录，本例程中为/taskdata目录。PARAMS字段设置所有的运行参数对应的环境变量、参数别名、参数类型、参数描述以及参数默认值，其中，参数类型共有五种可用类型，如下列举所示：

1. string：字符串类型，当运行参数为文本类型时使用；
2. file：文件/文件夹类型，当运行参数需要输入文件或文件夹路径时使用；
3. number：数字类型，当运行参数为整数或者浮点数时使用；
4. enum：枚举类型，当运行参数限制只能在若干个选项中选择一个时使用，注意必须配合选项字段，要输入枚举选项的列表；
5. boolean：布尔类型，当运行参数只有两种情况时可以使用，适用于类checkbox的情况。

本例程中算法内部共接收两个参数，对应的环境变量分别为DATA_PATH与PARAMS，且DATA_PATH需要用户输入文件的路径，而PARAMS则为字符串类型，故最后的params.json文件应如下所示：

```json
#---------------------------计算平台模块参数模板文件说明----------------------------#
#    按照尖括号内的说明替换尖括号内的值，并删除尖括号
#    请不要删除任何字段，删除任何字段均会导致模板无法通过格式检查
#    PARAMS字段中的每一项都是一个运行参数，每一项的键为参数名，值为参数值类型和参数描述
#    请确保运行参数名称唯一，且在Docker镜像文件的环境变量中，否则无法通过参数一致性检查
#-----------------------------------------------------------------------------#

{
    "TASKFILES_DIR": "/taskdata",
    "PARAMS": {
        "DATA_PATH": [
            "数据文件路径",
            "file",
            "需要分析的文件相对于任务目录的路径",
            "test.txt"
        ],
        "PARAMS": [
            "运行参数",
            "string",
            "算法的某个运行参数",
            "params"
        ]
    }
}
```

需要注意的是，当值类型设置为enum时，需要保留运行参数的选项字段，且必须要为列表类型。

编辑完成后，保存即可。

### 3.5 移动Docker镜像归档文件

将2.4步骤中导出的镜像归档文件复制或移动到功能模块模板目录下即可。复制后的功能模块模版目录应包括metadata.json、params.json以及image.tar共三个文件。

### 3.6 封装功能模块

在功能模块模板目录的上一级目录执行cpm pack <folder_name>即可将整个编辑完成的模板目录打包为功能模块文件，并输出在当前工作目录下。在封装过程中，封装工具会对metadata.json与params.json两个文件进行格式检查，并检查params.json文件中定义的环境变量是否与Docker镜像中的环境变量一致，确保功能模块能够正常工作。如果上述检查未通过，则无法封装为功能模块文件。

