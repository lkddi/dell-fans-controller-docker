FROM debian:bookworm-slim
LABEL maintainer="lkddi"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装运行所需的最小Debian依赖并设置容器时区，兼顾体积和ipmitool兼容性
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ipmitool \
        python3 \
        tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo "${TZ}" > /etc/timezone

# 只复制运行所需源码，避免文档和仓库元数据进入镜像
WORKDIR /dell-fans-controller
COPY controller ./controller
COPY start.py ./

# 设置启动命令
CMD ["python3", "start.py"]
