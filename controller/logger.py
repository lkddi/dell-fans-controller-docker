import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# 自定义日志格式器：统一输出北京时间，方便容器日志排查
class CustomFormatter(logging.Formatter):
    # 格式化日志记录并注入北京时间字段
    def format(self, record):
        desired_timezone = timezone(timedelta(hours=8))
        current_time = datetime.now(desired_timezone).strftime('%Y-%m-%d %H:%M:%S')
        record.customtime = current_time
        return super().format(record)


# 标准输出日志处理器：让Docker日志直接显示控制器运行状态
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter(' %(customtime)s [%(levelname)s] %(message)s'))
logger.addHandler(stream_handler)
