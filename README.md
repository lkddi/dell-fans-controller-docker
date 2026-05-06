# Dell Fans Controller / Dell 风扇控制器

Dockerized fan controller for Dell iDRAC/IPMI servers. It reads temperature sensors through `ipmitool` and adjusts fan speed automatically to reduce noise while keeping the server safe.

通过 iDRAC/IPMI 自动读取 Dell 服务器温度，并根据温度调整风扇转速。适合希望降低噪音、但仍保留高温自动保护的家庭实验室、机房和 NAS 场景。

This project is upgraded and developed based on [joestar817/dell-fans-controller-docker](https://github.com/joestar817/dell-fans-controller-docker).

本项目基于 [joestar817/dell-fans-controller-docker](https://github.com/joestar817/dell-fans-controller-docker) 升级开发。

> Warning: manual fan control can cause overheating if configured incorrectly. Test with care and keep iDRAC automatic mode available as fallback.
>
> 警告：手动风扇控制配置不当可能导致过热。请先确认服务器散热状态，并保留 iDRAC 自动模式作为兜底。

## Features / 功能

- Reads Dell iDRAC sensor data with IPMI LANPlus.
- Automatically switches between manual fan speed and iDRAC automatic mode.
- Reuses sensor data within one control cycle to reduce iDRAC session pressure.
- Retries transient IPMI session failures and backs off after controller errors.
- Supports Docker multi-arch images: `linux/amd64` and `linux/arm64`.

- 通过 IPMI LANPlus 读取 Dell iDRAC 传感器数据。
- 根据最高温度自动设置风扇转速，超过阈值时交还 iDRAC 自动控制。
- 单次控制周期复用传感器数据，减少 iDRAC 会话压力。
- 对临时 IPMI 会话失败进行重试，并在控制器异常后等待下一轮。
- Docker 镜像支持 `linux/amd64` 和 `linux/arm64`。

## Tested Environment / 已测试环境

This project has been tested on Dell PowerEdge R730xd with iDRAC8.

本项目已在 Dell PowerEdge R730xd 服务器的 iDRAC8 环境中测试使用。

## Quick Start / 快速开始

Before running, enable IPMI over LAN in iDRAC and make sure the host running this container can reach the iDRAC management IP.

运行前请先在 iDRAC 中启用 IPMI over LAN，并确认运行容器的主机可以访问 iDRAC 管理 IP。

### Docker

```bash
docker run -d --name dell-fans-controller \
  --restart always \
  -e HOST=192.168.1.100 \
  -e USERNAME=root \
  -e PASSWORD=your_idrac_password \
  -e FAN_SPEED_STEPS=50:20,55:25,60:30,65:40 \
  -e CONTROL_INTERVAL_SECONDS=120 \
  -e ERROR_INTERVAL_SECONDS=120 \
  -e IPMI_FAILURE_BACKOFF_SECONDS=300 \
  -e IPMI_RETRY_COUNT=5 \
  -e IPMI_RETRY_DELAY_SECONDS=20 \
  -e IPMI_TIMEOUT_SECONDS=60 \
  -e USE_RAW_FAN_DUTY=false \
  lkddi/dell-fans-controller:latest
```

View logs / 查看日志：

```bash
docker logs -f dell-fans-controller
```

### Docker Compose

Copy the example environment file and edit the iDRAC settings:

复制示例环境变量文件，并修改 iDRAC 配置：

```bash
cp .env.example .env
```

`.env` example / 示例：

```env
HOST=192.168.1.100
USERNAME=root
PASSWORD=your_idrac_password
FAN_SPEED_STEPS=50:20,55:25,60:30,65:40
CONTROL_INTERVAL_SECONDS=120
ERROR_INTERVAL_SECONDS=120
IPMI_FAILURE_BACKOFF_SECONDS=300
IPMI_RETRY_COUNT=5
IPMI_RETRY_DELAY_SECONDS=20
IPMI_TIMEOUT_SECONDS=60
USE_RAW_FAN_DUTY=false
```

Start the service / 启动服务：

```bash
docker compose up -d
```

Docker Compose reads all options from `.env`, including fan policy and IPMI retry settings.

Docker Compose 会从 `.env` 读取全部配置，包括温控档位和 IPMI 重试参数。

### Run with Python / 直接使用 Python 运行

Install dependencies / 安装依赖：

```bash
# Debian / Ubuntu
sudo apt update
sudo apt install -y ipmitool python3

# macOS with Homebrew
brew install ipmitool python
```

Run / 运行：

```bash
export HOST=192.168.1.100
export USERNAME=root
export PASSWORD=your_idrac_password
export FAN_SPEED_STEPS=50:20,55:25,60:30,65:40
export CONTROL_INTERVAL_SECONDS=120
export ERROR_INTERVAL_SECONDS=120
export IPMI_FAILURE_BACKOFF_SECONDS=300
export IPMI_RETRY_COUNT=5
export IPMI_RETRY_DELAY_SECONDS=20
export IPMI_TIMEOUT_SECONDS=60
export USE_RAW_FAN_DUTY=false
python3 start.py
```

## Configuration / 配置

| Variable | Required | Description |
| --- | --- | --- |
| `HOST` | Yes | iDRAC management IP address. / iDRAC 管理 IP。 |
| `USERNAME` | Yes | iDRAC username with IPMI permission. / 有 IPMI 权限的 iDRAC 用户名。 |
| `PASSWORD` | Yes | iDRAC password. / iDRAC 密码。 |
| `FAN_SPEED_STEPS` | No | Temperature-to-speed rules. Default: `50:20,55:25,60:30,65:40`. / 温度和风扇转速规则，默认值：`50:20,55:25,60:30,65:40`。 |
| `CONTROL_INTERVAL_SECONDS` | No | Normal control interval. Default: `120`. / 正常控制间隔，默认 `120` 秒。 |
| `ERROR_INTERVAL_SECONDS` | No | Wait time after a failed control cycle. Default: same as `CONTROL_INTERVAL_SECONDS`. / 控制周期失败后的等待时间，默认等于正常控制间隔。 |
| `IPMI_FAILURE_BACKOFF_SECONDS` | No | Cooldown after all IPMI retries fail. Default: `300`. / 单轮 IPMI 重试全部失败后的冷却时间，默认 `300` 秒。 |
| `IPMI_RETRY_COUNT` | No | Retry count for each IPMI command. Default: `5`. / 单条 IPMI 命令重试次数，默认 `5`。 |
| `IPMI_RETRY_DELAY_SECONDS` | No | Wait time between IPMI retries. Default: `20`. / IPMI 重试间隔，默认 `20` 秒。 |
| `IPMI_TIMEOUT_SECONDS` | No | Subprocess timeout for each IPMI command. Default: `60`. / 单次 IPMI 命令超时时间，默认 `60` 秒。 |
| `USE_RAW_FAN_DUTY` | No | Query raw fan duty before RPM estimation. Default: `false`. / 是否先用 raw 命令读取风扇占空比，默认 `false`。 |

The application does not include default credentials. Missing variables will stop startup with a clear error.

程序不内置默认地址、账号或密码。缺少环境变量时会直接停止并输出明确错误。

For iDRAC8 systems with unstable IPMI sessions, keep `CONTROL_INTERVAL_SECONDS` at `120` or higher. The default `USE_RAW_FAN_DUTY=false` avoids one extra IPMI session per cycle and estimates fan percentage from the RPM data already returned by `sdr`.

对于 IPMI 会话不稳定的 iDRAC8，建议 `CONTROL_INTERVAL_SECONDS` 保持 `120` 秒或更高。默认 `USE_RAW_FAN_DUTY=false` 会跳过额外的 raw 占空比查询，直接使用同一次 `sdr` 返回的 RPM 估算风扇百分比，减少 iDRAC 会话压力。

## Temperature Policy / 温控策略

The controller reads all temperature sensors and uses the highest value.

控制器读取所有温度传感器，并使用最高温度作为控制依据。

| Temperature / 温度 | Fan Speed / 风扇转速 |
| --- | --- |
| `0-50 C` | `20%` |
| `50-55 C` | `25%` |
| `55-60 C` | `30%` |
| `60-65 C` | `40%` |
| `>65 C` | iDRAC automatic mode / iDRAC 自动模式 |

Customize the policy with `FAN_SPEED_STEPS`. Each item uses `temperature:speed`, separated by commas. The controller sorts thresholds from low to high. When the current highest temperature is greater than the last threshold, it switches to iDRAC automatic mode.

可以通过 `FAN_SPEED_STEPS` 自定义温控策略。每一项格式为 `温度:转速`，多项用英文逗号分隔。控制器会按温度阈值从低到高排序；当最高温度超过最后一个阈值时，自动切回 iDRAC 自动模式。

Invalid values stop startup with a clear error. Fan speed must be an integer from `10` to `100`, and temperature thresholds cannot be duplicated.

配置错误会在启动时直接报错退出。风扇转速必须是 `10` 到 `100` 的整数，温度阈值不能重复。

Example / 示例：

```env
FAN_SPEED_STEPS=45:20,55:30,62:45,70:60
```

This means / 含义：

| Temperature / 温度 | Fan Speed / 风扇转速 |
| --- | --- |
| `0-45 C` | `20%` |
| `45-55 C` | `30%` |
| `55-62 C` | `45%` |
| `62-70 C` | `60%` |
| `>70 C` | iDRAC automatic mode / iDRAC 自动模式 |

## Troubleshooting / 故障排查

Test IPMI manually first / 先手动测试 IPMI：

```bash
ipmitool -H 192.168.1.100 -I lanplus -U root -P your_idrac_password mc info
ipmitool -H 192.168.1.100 -I lanplus -U root -P your_idrac_password sdr
```

Common issues / 常见问题：

- `Unable to establish IPMI v2 / RMCP+ session`: iDRAC IPMI service may be busy or unstable. Occasional retries are expected on some iDRAC8 systems. If all retries fail, the controller skips that cycle and waits for `IPMI_FAILURE_BACKOFF_SECONDS`.
- `Unable to establish IPMI v2 / RMCP+ session`：iDRAC IPMI 服务可能繁忙或不稳定。部分 iDRAC8 偶发重试是正常现象；如果单轮重试全部失败，控制器会跳过本轮并按 `IPMI_FAILURE_BACKOFF_SECONDS` 冷却等待。
- Frequent IPMI session failures / 频繁 IPMI 会话失败：check network latency, duplicate monitoring scripts or duplicate containers, and consider resetting iDRAC with `mc reset cold`.
- Connection failed / 连接失败：确认容器主机能访问 iDRAC 管理 IP。
- Authentication failed / 认证失败：确认用户名、密码和 IPMI 权限。
- Permission denied / 权限不足：建议使用专用 iDRAC 用户，并授予 IPMI 控制权限。

## Release / 发布新版本

Docker images are published only from Git tags matching `v*`. Pull requests build and verify the image, while direct `master` pushes do not trigger Docker builds.

Docker 镜像只在推送 `v*` tag 时发布。PR 会做构建验证，直接推送 `master` 不触发 Docker 构建。

```bash
git tag v1.0.0
git push origin v1.0.0
```

The tag workflow publishes:

- `lkddi/dell-fans-controller:latest`
- `lkddi/dell-fans-controller:v1.0.0`
- `lkddi/dell-fans-controller:1.0.0`
- `lkddi/dell-fans-controller:1.0`
- `lkddi/dell-fans-controller:1`

GitHub Actions requires these repository secrets:

- `DOCKER_USER`: Docker Hub username.
- `DOCKER_PASS`: Docker Hub access token. Do not use your account password.

## Development / 开发

Syntax check without generating tracked cache files:

```bash
python3 -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(), filename=p) for p in ['start.py','controller/client.py','controller/ipmi.py']]"
```

Build locally:

```bash
docker build -t lkddi/dell-fans-controller:test .
```

## License / 许可证

MIT
