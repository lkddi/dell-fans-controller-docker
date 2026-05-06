import os
import time
import traceback

from controller.client import FanController
from controller.logger import logger

if __name__ == '__main__':

    # 从环境变量读取iDRAC连接信息，开源版本不内置任何真实默认凭据
    host = os.getenv('HOST')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    if not host:
        raise RuntimeError('未设置 HOST 环境变量')

    if not username:
        raise RuntimeError('未设置 USERNAME 环境变量')

    if not password:
        raise RuntimeError('未设置 PASSWORD 环境变量')

    # 复用控制器实例，避免每轮循环丢失上次设置状态
    client = FanController(host=host, username=username, password=password)

    while True:
        try:            
            # 执行一次温度读取和风扇控制周期
            client.run()
            time.sleep(60)
        except Exception as err:
            logger.error(
                f'运行控制器失败 {err}. {traceback.format_exc()}'
            )
            # iDRAC会话异常时等待下一轮，避免连续请求压垮IPMI服务
            time.sleep(60)
