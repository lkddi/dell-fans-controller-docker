# Changelog / 更新日志

## Unreleased

- 准备公开开源发布流程，Docker Hub 镜像统一为 `lkddi/dell-fans-controller`。
- 说明项目基于 `joestar817/dell-fans-controller-docker` 升级开发。
- GitHub Actions 改为 PR 构建验证，`v*` tag 才发布 Docker 镜像。
- 新增 Docker、Docker Compose 和本机 Python 三种运行说明。
- 移除代码中的默认 iDRAC 地址、账号和密码，改为必须通过环境变量配置。
- 增加 `.env.example`、`.dockerignore` 和 MIT License。
- 清理 Python 缓存文件，避免将运行产物提交到仓库。
- Docker 运行镜像切换到 Debian slim，只安装 `python3`、`ipmitool` 和时区数据，在降低体积的同时保留更好的IPMI兼容性。
- 新增 `FAN_SPEED_STEPS` 环境变量，允许用户通过 `.env` 自定义温度阈值和风扇转速档位。
- 新增轮询间隔、IPMI重试、命令超时和 raw 风扇占空比查询开关，默认减少 iDRAC8 的会话压力。
- 单轮 IPMI 重试全部失败时改为冷却跳过，并避免重复发送手动模式切换 raw 命令。

## Previous Improvements

- 使用 `ipmitool sdr` 读取温度和风扇传感器数据。
- 根据最高温度自动选择风扇转速，高温时交还 iDRAC 自动模式。
- 对 IPMI 会话失败和命令超时增加重试和日志。
- 使用 RPM 估算风扇百分比，降低部分 Dell 机型 raw 命令返回 0 时的影响。
