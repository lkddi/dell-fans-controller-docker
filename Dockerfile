FROM alpine:3.20
LABEL maintainer="lkddi"

ENV TZ=Asia/Shanghai \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 安装运行所需的最小依赖并设置容器时区
RUN apk add --no-cache \
        ipmitool \
        python3 \
        tzdata \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo "${TZ}" > /etc/timezone

# 只复制运行所需源码，避免文档和仓库元数据进入镜像
WORKDIR /dell-fans-controller
COPY controller ./controller
COPY start.py ./

# 设置启动命令
CMD ["python3", "start.py"]
