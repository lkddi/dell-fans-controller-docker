from controller.logger import logger

from controller.ipmi import IpmiTool


DEFAULT_FAN_SPEED_STEPS = (
    (50, 20),
    (55, 25),
    (60, 30),
    (65, 40),
)


# 风扇控制器：根据iDRAC温度传感器结果自动切换风扇模式和转速
class FanController:

    # 初始化控制器并记录iDRAC连接信息
    def __init__(self, host: str, username: str, password: str, fan_speed_steps: str = None):
        self.host = host
        self.username = username
        self.password = password

        self.ipmi = IpmiTool(self.host, self.username, self.password)
        self.fan_speed_steps = self.parse_fan_speed_steps(fan_speed_steps)
        self.last_set_speed = None  # 记录最后设置的风扇速度
        self.is_auto_mode = False   # 记录当前是否为自动模式

    # 解析温控规则配置，格式为 "50:20,55:25,60:30,65:40"
    def parse_fan_speed_steps(self, steps: str) -> tuple:
        """
        解析环境变量中的温控规则
        :param steps: 温度阈值和风扇转速配置
        :return: 按温度升序排列的规则元组
        """
        if steps is None:
            return DEFAULT_FAN_SPEED_STEPS

        if not steps.strip():
            raise ValueError('FAN_SPEED_STEPS 至少需要包含一条温控规则')

        parsed_rules = []
        for item in steps.split(','):
            item = item.strip()
            if not item:
                continue

            try:
                temperature_text, speed_text = item.split(':', 1)
                temperature = int(temperature_text.strip())
                speed = int(speed_text.strip())
            except ValueError as exc:
                raise ValueError(
                    f'FAN_SPEED_STEPS 格式错误: {steps}，正确示例: 50:20,55:25,60:30,65:40'
                ) from exc

            if temperature <= 0:
                raise ValueError('FAN_SPEED_STEPS 温度阈值必须大于0')

            if speed < 10 or speed > 100:
                raise ValueError('FAN_SPEED_STEPS 风扇转速必须在10到100之间')

            parsed_rules.append((temperature, speed))

        if not parsed_rules:
            raise ValueError('FAN_SPEED_STEPS 至少需要包含一条温控规则')

        parsed_rules.sort(key=lambda rule: rule[0])
        temperatures = [rule[0] for rule in parsed_rules]
        if len(temperatures) != len(set(temperatures)):
            raise ValueError('FAN_SPEED_STEPS 不能包含重复的温度阈值')

        return tuple(parsed_rules)

    # 设置手动风扇速度
    def set_fan_speed(self, speed: int):
        logger.info(f'设置风扇速度: {speed}%')
        self.ipmi.set_fan_speed(speed)

    # 根据最高温度计算目标风扇转速
    def get_required_fan_speed(self, temperature: int) -> int:
        """
        根据温度确定所需的风扇转速
        :param temperature: 当前最高温度
        :return: 对应的风扇转速百分比，如果应该切换到自动模式则返回-1
        """
        for threshold, speed in self.fan_speed_steps:
            if 0 < temperature <= threshold:
                return speed

        return -1  # 表示应切换到自动模式

    # 执行一次完整的温度读取和风扇控制周期
    def run(self):
        # 同一轮控制周期复用一次SDR结果，减少iDRAC会话压力
        sensor_data = self.ipmi.sensor()
        temperature: int = max(self.ipmi.temperature(sensor_data))
        logger.info(f'当前最高温度: {temperature}')

        required_speed = self.get_required_fan_speed(temperature)

        if required_speed == -1:
            # 需要切换到自动模式
            if not self.is_auto_mode:
                logger.info(f'切换风扇为自动模式')
                self.ipmi.switch_fan_mode(auto=True)
                self.is_auto_mode = True
                self.last_set_speed = None  # 重置手动设置的速度
            else:
                logger.info(f'当前已是自动模式，无需操作')
        else:
            # 需要设置手动风扇速度
            if self.is_auto_mode:
                # 如果当前是自动模式，需要先切换到手动模式
                logger.info(f'从自动模式切换到手动模式')
                self.ipmi.switch_fan_mode(auto=False)
                self.is_auto_mode = False

            # 获取当前风扇转速
            current_speed = self.ipmi.get_fan_duty_cycle(sensor_data)

            # 只有在当前转速与所需转速不同时才调整
            # 如果无法获取当前转速（返回-1），则检查是否已记录之前设置的速度
            if current_speed == -1:
                logger.warning('无法获取当前风扇转速，为避免IPMI会话不稳定时盲目写入，本轮跳过设置')
            elif current_speed != required_speed:
                logger.info(f'当前风扇转速: {current_speed}%, 需要转速: {required_speed}%')
                self.set_fan_speed(required_speed)
                self.last_set_speed = required_speed
            else:
                logger.info(f'当前风扇转速: {current_speed}% 已符合要求，无需调整')
