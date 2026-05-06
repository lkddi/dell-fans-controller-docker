# Changelog / 更新日志

## Unreleased

- 准备公开开源发布流程，Docker Hub 镜像统一为 `lkddi/dell-fans-controller`。
- GitHub Actions 改为 PR/master 构建验证，`v*` tag 才发布 Docker 镜像。
- 新增 Docker、Docker Compose 和本机 Python 三种运行说明。
- 移除代码中的默认 iDRAC 地址、账号和密码，改为必须通过环境变量配置。
- 增加 `.env.example`、`.dockerignore` 和 MIT License。
- 清理 Python 缓存文件，避免将运行产物提交到仓库。

## Previous Improvements

- 使用 `ipmitool sdr` 读取温度和风扇传感器数据。
- 根据最高温度自动选择风扇转速，高温时交还 iDRAC 自动模式。
- 对 IPMI 会话失败和命令超时增加重试和日志。
- 使用 RPM 估算风扇百分比，降低部分 Dell 机型 raw 命令返回 0 时的影响。
