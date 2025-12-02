# Dell风扇控制器

## 项目简介

Dell风扇控制器是一个自动化工具，通过IPMI接口监控Dell服务器的温度并自动调节风扇转速。本项目基于原项目 joestar817/dell-fans-controller-docker 进行了大量改进和功能增强。

### 主要特性

- **精准温度监控**：通过IPMI接口获取服务器进出口、CPU等关键温度数据
- **智能转速控制**：根据温度自动调节风扇转速，平衡散热效果和噪音
- **网络容错能力**：具备强大的网络连接容错机制，能处理网络波动
- **多架构支持**：支持 AMD64 和 ARM64 架构，兼容多种平台
- **自动构建部署**：通过 GitHub Actions 自动构建和推送 Docker 镜像

## 使用方法

### 1. 准备工作

在开始使用之前，请确保：

1. 登录iDRAC管理界面并启用IPMI服务
2. 确保网络能够访问iDRAC管理接口
3. 准备好iDRAC的用户名和密码

### 2. Docker运行

```bash
# 基本运行命令
docker run -d --name=dell-fans-controller \
  -e HOST=YOUR_IDRAC_IP \
  -e USERNAME=YOUR_USERNAME \
  -e PASSWORD=YOUR_PASSWORD \
  --restart always \
  lkddi/dell-fans-controller:latest
```

### 3. 配置参数

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| HOST | iDRAC管理接口IP地址 | 10.10.11.11 |
| USERNAME | iDRAC用户名 | root |
| PASSWORD | iDRAC密码 | ddmabc123 |

## 工作原理

### 温度控制策略

系统会监控服务器的多个温度传感器，取最高温度值作为控制依据：

| 温度范围(℃) | 风扇转速(%) | 说明 |
|------------|------------|------|
| 0-50 | 15 | 静音模式 |
| 50-55 | 20 | 低速运行 |
| 55-60 | 30 | 中速运行 |
| 60-65 | 40 | 高速运行 |
| >65 | 自动模式 | 由iDRAC自动调节 |

### 智能控制机制

- **模式切换**：系统在手动模式和自动模式间智能切换
- **转速监测**：实时监测当前风扇转速，避免不必要的调整
- **状态跟踪**：记录和跟踪风扇模式和转速设置历史

## Docker镜像

### 支持的架构

- AMD64 (x86_64)
- ARM64 (aarch64)

### 镜像仓库

- Docker Hub: `lkddi/dell-fans-controller:latest`
- Harbor: `harbor.ay.lc/library/dell-fans-controller:latest`

### 自动构建

项目通过 GitHub Actions 实现了自动构建和部署：

- 每次推送代码到master分支时自动构建新镜像
- 支持多架构镜像构建
- 自动推送至Docker Hub和Harbor仓库

## 技术实现

### 核心功能

1. **精确的温度读取**：使用正则表达式解析IPMI传感器数据，准确提取温度值
2. **RPM到百分比转换**：通过校准数据建立RPM与风扇转速百分比的准确转换关系（20% = 4800 RPM）
3. **网络容错机制**：
   - 5次重试机制
   - 60秒超时设置
   - IPMI会话建立失败的特殊处理
   - 10秒重试间隔

### 配置选项

- 运行间隔：每60秒检查一次温度并调整风扇转速
- 网络超时：60秒超时限制
- 重试机制：5次失败后停止

## 部署示例

### Proxmox VE (PVE)

```bash
docker run -d --name=dell-fans-controller \
  -e HOST=192.168.1.100 \
  -e USERNAME=root \
  -e PASSWORD=calvin \
  --restart always \
  lkddi/dell-fans-controller:latest
```

### 群晖NAS

在群晖的Docker应用中：

1. 搜索并下载 `lkddi/dell-fans-controller` 镜像
2. 创建容器并设置环境变量
3. 启用自动重启选项

## 安全说明

- 项目使用IPMI协议与服务器通信，需要相应的管理权限
- 建议使用专用的IPMI管理账户
- 定期更新镜像以获得安全补丁

## 故障排除

### 常见问题

1. **连接失败**：检查网络是否能访问iDRAC接口
2. **认证失败**：确认用户名和密码正确
3. **权限不足**：确保账户有IPMI控制权限

### 日志查看

```bash
docker logs dell-fans-controller
```

## 免责声明

手动调整服务器风扇转速可能带来过热风险，使用本项目前请充分了解风险并做好数据备份。对于使用本项目引发的任何问题，作者概不负责。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

该项目遵循原项目的开源协议。