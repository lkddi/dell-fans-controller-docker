import os
import time

from controller.client import FanController
from controller.logger import logger


# 解析整数环境变量，缺省时使用默认值
def get_int_env(name: str, default: int, min_value: int = 1) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise RuntimeError(f'{name} 必须是整数') from exc

    if parsed_value < min_value:
        raise RuntimeError(f'{name} 必须大于等于 {min_value}')

    return parsed_value


# 解析布尔环境变量，支持 true/false、1/0、yes/no
def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized_value = value.strip().lower()
    if normalized_value in ('1', 'true', 'yes', 'on'):
        return True

    if normalized_value in ('0', 'false', 'no', 'off'):
        return False

    raise RuntimeError(f'{name} 必须是布尔值: true/false')


if __name__ == '__main__':

    # 从环境变量读取iDRAC连接信息，开源版本不内置任何真实默认凭据
    host = os.getenv('HOST')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    # 优先读取新的温控档位变量，并兼容旧别名
    fan_speed_steps = os.getenv('FAN_SPEED_STEPS')
    if fan_speed_steps is None:
        fan_speed_steps = os.getenv('FAN_SPEED_RULES')
    control_interval = get_int_env('CONTROL_INTERVAL_SECONDS', 120)
    error_interval = get_int_env('ERROR_INTERVAL_SECONDS', control_interval)
    ipmi_failure_backoff = get_int_env('IPMI_FAILURE_BACKOFF_SECONDS', 300)
    ipmi_retry_count = get_int_env('IPMI_RETRY_COUNT', 5)
    ipmi_retry_delay = get_int_env('IPMI_RETRY_DELAY_SECONDS', 20)
    ipmi_timeout = get_int_env('IPMI_TIMEOUT_SECONDS', 60)
    use_raw_fan_duty = get_bool_env('USE_RAW_FAN_DUTY', False)
    if not host:
        raise RuntimeError('未设置 HOST 环境变量')

    if not username:
        raise RuntimeError('未设置 USERNAME 环境变量')

    if not password:
        raise RuntimeError('未设置 PASSWORD 环境变量')

    # 复用控制器实例，避免每轮循环丢失上次设置状态
    client = FanController(
        host=host,
        username=username,
        password=password,
        fan_speed_steps=fan_speed_steps,
        ipmi_retry_count=ipmi_retry_count,
        ipmi_retry_delay=ipmi_retry_delay,
        ipmi_timeout=ipmi_timeout,
        use_raw_fan_duty=use_raw_fan_duty,
    )

    while True:
        try:            
            # 执行一次温度读取和风扇控制周期
            client.run()
            time.sleep(control_interval)
        except RuntimeError as err:
            logger.warning(
                f'本轮IPMI控制失败，跳过本轮并等待 {ipmi_failure_backoff} 秒: {err}'
            )
            # 连续会话失败时给iDRAC更长恢复窗口，避免马上进入下一轮重试
            time.sleep(ipmi_failure_backoff)
        except Exception as err:
            logger.error(f'运行控制器失败 {err}', exc_info=True)
            # iDRAC会话异常时等待下一轮，避免连续请求压垮IPMI服务
            time.sleep(error_interval)
