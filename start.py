import os
import time
import traceback

from controller.client import FanController
from controller.logger import logger

if __name__ == '__main__':

    host = os.getenv('HOST', "10.10.11.11")
    username = os.getenv('USERNAME', "root")
    password = os.getenv('PASSWORD', "ddmabc123")
    if not host:
        raise RuntimeError('未设置 HOST 环境变量')

    if not username:
        raise RuntimeError('未设置 USERNAME 环境变量')

    if not password:
        raise RuntimeError('未设置 PASSWORD 环境变量')

    while True:
        try:            
            client = FanController(host=host, username=username, password=password)
            client.run()
            time.sleep(60)
        except Exception as err:
            logger.error(
                f'运行控制器失败 {err}. {traceback.format_exc()}'
            )