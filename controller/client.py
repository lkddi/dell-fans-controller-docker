from controller.logger import logger

from controller.ipmi import IpmiTool


class FanController:

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password

        self.ipmi = IpmiTool(self.host, self.username, self.password)
        self.last_set_speed = None  # 记录最后设置的风扇速度
        self.is_auto_mode = False   # 记录当前是否为自动模式

    def set_fan_speed(self, speed: int):
        logger.info(f'设置风扇速度: {speed}%')
        self.ipmi.set_fan_speed(speed)

    def get_required_fan_speed(self, temperature: int) -> int:
        """
        根据温度确定所需的风扇转速
        :param temperature: 当前最高温度
        :return: 对应的风扇转速百分比，如果应该切换到自动模式则返回-1
        """
        if 0 < temperature <= 50:
            return 15
        elif 50 < temperature <= 55:
            return 20
        elif 55 < temperature <= 60:
            return 30
        elif 60 < temperature <= 65:
            return 40
        else:
            return -1  # 表示应切换到自动模式

    def run(self):
        temperature: int = max(self.ipmi.temperature())
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
            current_speed = self.ipmi.get_fan_duty_cycle()

            # 只有在当前转速与所需转速不同时才调整
            # 如果无法获取当前转速（返回-1），则检查是否已记录之前设置的速度
            if current_speed == -1:
                # 如果无法获取当前转速，但上次设置的速度与所需速度不同，则更新
                if self.last_set_speed != required_speed:
                    logger.info(f'无法获取当前风扇转速，但上次设置({self.last_set_speed}%)与需要({required_speed}%)不同，进行设置')
                    self.set_fan_speed(required_speed)
                    self.last_set_speed = required_speed
                else:
                    logger.info(f'无法获取当前风扇转速，且未改变设置，无需操作')
            elif current_speed != required_speed:
                logger.info(f'当前风扇转速: {current_speed}%, 需要转速: {required_speed}%')
                self.set_fan_speed(required_speed)
                self.last_set_speed = required_speed
            else:
                logger.info(f'当前风扇转速: {current_speed}% 已符合要求，无需调整')