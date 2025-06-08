import os
import time
import traceback

from controller.client import FanController
from controller.logger import logger

if __name__ == '__main__':

    host = os.getenv('HOST')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    if host is None:
        raise RuntimeError('HOST 环境变量未设置')

    if username is None:
        raise RuntimeError('USERNAME 环境变量未设置')

    if password is None:
        raise RuntimeError('PASSWORD 环境变量未设置')

    while True:
        try:
            client = FanController(host=host, username=username, password=password)
            client.run()
            time.sleep(60)
        except Exception as err:
            logger.error(
                f'运行控制器失败 {err}. {traceback.format_exc()}'
            )
