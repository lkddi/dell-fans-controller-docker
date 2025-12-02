### dell-fans-controller-docker



#### 项目说明

 本项目通过python脚本调用ipmitool，来自动调整Dell R730服务器的风扇转速，并打包为docker镜像。

 适用于在R730上搭建all in one服务场景，docker镜像可运行在pve、群晖，或其它支持docker的环境中



#### 使用说明

1. 请登录idrac打开ipmi服务

2. 运行以下命令
 ```
   docker run -d --name=dell-fans-controller-docker  -e HOST=192.168.1.1 -e USERNAME=root -e PASSWORD=password --restart always registry.cn-huhehaote.aliyuncs.com/lkddi_image/dell-fans-controller-docker:latest
   ```

、、、
docker run -d --name=dell-fans-controller-docker  -e HOST=10.10.11.11 -e USERNAME=root -e PASSWORD=ddmabc123 --restart always registry.cn-huhehaote.aliyuncs.com/lkddi_image/dell-fans-controller-docker:latest
、、、
   

#### 代码说明

脚本首先通过ipmitool来获取 **进出口温度和CPU核心温度**，再通过其中的最大值来判断调整服务器的风扇转速

### Docker 镜像构建

本项目通过 GitHub Actions 自动构建 Docker 镜像，并推送到 Docker Hub 和 Harbor 私有仓库。

- Docker Hub: `lkddi/dell-fans-controller:latest`
- Harbor: `harbor.ay.lc/library/dell-fans-controller:latest`

镜像支持多架构 (linux/amd64, linux/arm64)

运行间隔为每60秒运行一次

| 温度(℃) | 风扇转速(%)            |
|-------|--------------------|
| 0-50  | 15                 |
| 50-55 | 20                 |
| 55-60 | 30                 |
| 60-65 | 40                 |
| >65℃  | 设置为自动模式，由idrac自动调速 |



#### 免责声明

手动调整风扇转速有一定的风险导致服务器过热损坏，请谨慎操作，对此使用此项目引发的任何问题，概不负责
