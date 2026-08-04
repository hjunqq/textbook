# 附录A：常用开发工具与环境配置

本附录介绍智慧水利平台开发中常用的工具和环境配置方法，帮助读者快速搭建开发环境。

## 开发工具列表

### 集成开发环境(IDE)

| 工具名称 | 适用场景 | 下载地址 |
| ------- | ------- | ------- |
| Visual Studio Code | 前端开发、Python开发 | [https://code.visualstudio.com/](https://code.visualstudio.com/) |
| IntelliJ IDEA | Java开发 | [https://www.jetbrains.com/idea/](https://www.jetbrains.com/idea/) |
| Eclipse | Java开发 | [https://www.eclipse.org/](https://www.eclipse.org/) |
| PyCharm | Python开发 | [https://www.jetbrains.com/pycharm/](https://www.jetbrains.com/pycharm/) |

### 版本控制工具

| 工具名称 | 描述 | 下载地址 |
| ------- | --- | ------- |
| Git | 分布式版本控制系统 | [https://git-scm.com/](https://git-scm.com/) |
| GitHub Desktop | Git图形界面客户端 | [https://desktop.github.com/](https://desktop.github.com/) |
| TortoiseGit | Windows系统Git客户端 | [https://tortoisegit.org/](https://tortoisegit.org/) |

### 数据库工具

| 工具名称 | 适用数据库 | 下载地址 |
| ------- | -------- | ------- |
| MySQL Workbench | MySQL | [https://www.mysql.com/products/workbench/](https://www.mysql.com/products/workbench/) |
| Navicat | 多种数据库 | [https://www.navicat.com/](https://www.navicat.com/) |
| DBeaver | 多种数据库 | [https://dbeaver.io/](https://dbeaver.io/) |

## 环境配置指南

### Node.js环境配置

Node.js是前端开发的基础环境，下面是安装步骤：

1. 访问[Node.js官网](https://nodejs.org/)下载最新LTS版本
2. 运行安装程序，按照提示完成安装
3. 打开命令行工具，运行以下命令验证安装：

```bash
node -v
npm -v
```

### Java开发环境配置

1. 下载并安装JDK（Java Development Kit）
2. 配置环境变量：
   - JAVA_HOME：指向JDK安装目录
   - PATH：添加%JAVA_HOME%\bin
3. 验证安装：

```bash
java -version
javac -version
```

### Python环境配置

推荐使用Anaconda进行Python环境管理：

1. 下载并安装[Anaconda](https://www.anaconda.com/products/individual)
2. 创建虚拟环境：

```bash
conda create -n waterenv python=3.9
conda activate waterenv
```

3. 安装常用包：

```bash
pip install numpy pandas matplotlib flask django scikit-learn tensorflow
```

## 开发环境集成配置

### 前端开发环境

```bash
# 安装Vue CLI
npm install -g @vue/cli

# 创建新项目
vue create water-frontend

# 进入项目目录
cd water-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

### 后端开发环境(Spring Boot)

1. 使用Spring Initializr创建项目：[https://start.spring.io/](https://start.spring.io/)
2. 导入到IDE中
3. 配置application.properties文件
4. 运行项目

## 常见问题与解决方案

### npm安装包失败

```bash
# 清除npm缓存
npm cache clean -f

# 使用国内镜像
npm config set registry https://registry.npmmirror.com
```

### Maven依赖下载慢

修改Maven的settings.xml文件，添加国内镜像：

```xml
<mirrors>
  <mirror>
    <id>alimaven</id>
    <name>aliyun maven</name>
    <url>https://maven.aliyun.com/repository/public</url>
    <mirrorOf>central</mirrorOf>
  </mirror>
</mirrors>
```

### Python包安装问题

```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
``` 