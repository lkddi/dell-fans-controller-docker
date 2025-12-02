FROM ubuntu:22.04
LABEL maintainer="joestar817@foxmail.com"

# 安装依赖并设置时区
RUN apt update && apt install -y \
    ipmitool \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' > /etc/timezone

# 复制应用文件
COPY . /dell-fans-controller-docker
WORKDIR /dell-fans-controller-docker

# 如果有requirements.txt则安装Python依赖
# COPY requirements.txt .
# RUN pip3 install --no-cache-dir -r requirements.txt

# 暴露可能需要的端口（虽然这个应用不需要）
# EXPOSE 80

# 设置启动命令
CMD ["python3", "start.py"]

