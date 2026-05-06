# Dell Fans Controller / Dell 风扇控制器

Dockerized fan controller for Dell iDRAC/IPMI servers. It reads temperature sensors through `ipmitool` and adjusts fan speed automatically to reduce noise while keeping the server safe.

通过 iDRAC/IPMI 自动读取 Dell 服务器温度，并根据温度调整风扇转速。适合希望降低噪音、但仍保留高温自动保护的家庭实验室、机房和 NAS 场景。

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
```

Start the service / 启动服务：

```bash
docker compose up -d
```

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
python3 start.py
```

## Configuration / 配置

| Variable | Required | Description |
| --- | --- | --- |
| `HOST` | Yes | iDRAC management IP address. / iDRAC 管理 IP。 |
| `USERNAME` | Yes | iDRAC username with IPMI permission. / 有 IPMI 权限的 iDRAC 用户名。 |
| `PASSWORD` | Yes | iDRAC password. / iDRAC 密码。 |

The application does not include default credentials. Missing variables will stop startup with a clear error.

程序不内置默认地址、账号或密码。缺少环境变量时会直接停止并输出明确错误。

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

## Troubleshooting / 故障排查

Test IPMI manually first / 先手动测试 IPMI：

```bash
ipmitool -H 192.168.1.100 -I lanplus -U root -P your_idrac_password mc info
ipmitool -H 192.168.1.100 -I lanplus -U root -P your_idrac_password sdr
```

Common issues / 常见问题：

- `Unable to establish IPMI v2 / RMCP+ session`: iDRAC IPMI service may be busy or unstable. Check network latency, duplicate monitoring scripts, and consider resetting iDRAC with `mc reset cold`.
- Connection failed / 连接失败：确认容器主机能访问 iDRAC 管理 IP。
- Authentication failed / 认证失败：确认用户名、密码和 IPMI 权限。
- Permission denied / 权限不足：建议使用专用 iDRAC 用户，并授予 IPMI 控制权限。

## Release / 发布新版本

Docker images are published only from Git tags matching `v*`. Pull requests and `master` pushes only build and verify the image.

Docker 镜像只在推送 `v*` tag 时发布。PR 和 `master` 推送只做构建验证，不覆盖 `latest`。

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
