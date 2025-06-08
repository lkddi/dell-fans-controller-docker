from controller.logger import logger

from controller.ipmi import IpmiTool


class FanController:

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password

        self.ipmi = IpmiTool(self.host, self.username, self.password)

    def set_fan_speed(self, speed: int):
        logger.info(f'设置风扇速度: {speed}%')
        self.ipmi.set_fan_speed(speed)

    def run(self):
        temperature: int = max(self.ipmi.temperature())
        logger.info(f'当前最高温度: {temperature}')

        if 0 < temperature <= 50:
            self.set_fan_speed(15)
        elif 50 < temperature <= 55:
            self.set_fan_speed(20)
        elif 55 < temperature <= 60:
            self.set_fan_speed(30)
        elif 60 < temperature <= 65:
            self.set_fan_speed(40)
        else:
            logger.info(f'切换风扇控制到自动模式')
            self.ipmi.switch_fan_mode(auto=True)
