import subprocess
import time
import re
from controller.logger import logger

class IpmiTool:
    def __init__(self, host: str, username: str, password: str):
        if not host or not username or not password:
            raise ValueError("host, username and password must be provided")
        self.host = host
        self.username = username
        self.password = password

    def run_cmd(self, cmd: str) -> str:
        basecmd = f'ipmitool -H {self.host} -I lanplus -U {self.username} -P {self.password}'
        command = f'{basecmd} {cmd}'
        retry_count = 3  # 设置重试次数
        for attempt in range(retry_count):
            try:
                # print(f"Executing command: {command}")  # 添加调试信息
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)

                if result.returncode != 0:
                    raise RuntimeError(
                        f'IPMI 命令执行失败: {cmd}\n错误详情: {result.stderr}'  # 更清晰的错误提示
                    )
                    # 添加网络和认证排查提示
                    print("请检查以下内容：")
                    print("1. 确保 BMC 地址可访问（ping 测试或网络配置）。")
                    print("2. 验证用户名、密码是否正确。")
                    print("3. 检查目标设备的 IPMI 功能是否启用。")

                return result.stdout
            except subprocess.TimeoutExpired:
                if attempt < retry_count - 1:
                    logger.warning(f'命令超时，正在重试... (尝试次数 {attempt + 1}/{retry_count})')
                    time.sleep(5)  # 每次重试前等待 5 秒
                else:
                    raise RuntimeError('IPMI 命令超时。请检查网络连接或服务器状态。')  # 更明确的错误提示

    def mc_info(self) -> str:
        """
        execute ipmitool command mc info
        :return:
        """
        return self.run_cmd(cmd='mc info')

    def sensor(self) -> str:
        """
        execute ipmitool command sdr to get sensor data
        :return:
        """
        return self.run_cmd(cmd='sdr')

    def temperature(self) -> list:
        """
        get current temperature
        :return:
        """
        data = self.sensor()
        temperatures = []
        import re

        for line in data.splitlines():
            if 'Temp' in line and 'degrees C' in line:
                # 提取温度值，例如从 " 25 degrees C" 中提取 25
                temp_part = line.split('|')[1]  # 获取中间列的内容
                # 使用正则表达式提取数字
                match = re.search(r'(\d+(\.\d+)?)\s+degrees C', temp_part)
                if match:
                    temp_value = float(match.group(1))
                    temperatures.append(temp_value)

        return temperatures

    def fan_speeds(self) -> list:
        """
        get current fan speeds
        :return: list of fan speeds in percentage
        """
        data = self.sensor()
        fan_speeds = []

        for line in data.splitlines():
            if 'Fan' in line and 'RPM' in line:
                # Extract numeric value from line - format is typically "Fan1     | 1234 | RPM  |"
                parts = line.split('|')
                if len(parts) >= 2:
                    try:
                        # Extract the value and convert RPM to percentage if possible
                        # For Dell servers, we may need to get duty cycle instead
                        value_str = parts[1].strip()
                        if value_str.isdigit():
                            rpm = int(value_str)
                            # Placeholder: we might need to use raw commands to get duty cycle
                            # For now, return the raw value
                            fan_speeds.append(rpm)
                    except ValueError:
                        continue
        return fan_speeds

    def get_fan_duty_cycle(self) -> int:
        """
        get current fan duty cycle/percentage
        :return: current fan duty cycle in percentage
        """
        try:
            # Raw command to get current fan duty cycle
            result = self.run_cmd('raw 0x30 0x31 0x01')
            # Parse the hex result to get duty cycle
            result_parts = result.strip().split()
            if result_parts and len(result_parts) >= 1:
                # The command should return a hex value representing the duty cycle
                duty_cycle_hex = result_parts[-1]
                duty_cycle = int(duty_cycle_hex, 16)
                # Ensure the value is in valid range (0-100)
                if 0 <= duty_cycle <= 100 and duty_cycle != 0:
                    # If we get a reasonable value (not 0), return it
                    return duty_cycle
                elif duty_cycle == 0:
                    # Value of 0 might indicate auto mode or that raw command doesn't return duty cycle on this system
                    logger.info('原始命令返回0，尝试从RPM估算风扇百分比')
        except Exception as e:
            logger.warning(f'获取风扇占空比的原始命令失败: {e}')

        # If raw command fails or returns 0, get fan speeds from sensor data and convert to approximate percentage
        try:
            data = self.sensor()
            fan_rpm_values = []
            import re

            for line in data.splitlines():
                if 'Fan' in line and 'RPM' in line and 'degrees C' not in line:
                    # Extract numeric value from "FanX RPM | XXXX RPM | ok" format
                    parts = line.split('|')
                    if len(parts) >= 2:
                        rpm_part = parts[1].strip()
                        # Use regex to extract RPM value
                        rpm_match = re.search(r'(\d+)\s+RPM', rpm_part)
                        if rpm_match:
                            rpm_value = int(rpm_match.group(1))
                            fan_rpm_values.append(rpm_value)

            if fan_rpm_values:
                # Calculate average RPM
                avg_rpm = sum(fan_rpm_values) / len(fan_rpm_values)

                # Based on calibration: 20% setting results in 4800 RPM
                # Therefore, 100% would theoretically be 24000 RPM (4800 * 5)
                # This seems high for typical server fans, but we'll use the calibrated ratio
                # When 20% = 4800 RPM, the percentage = (current_rpm / 4800) * 20
                calibrated_rpm_at_20_percent = 4800
                calibrated_percentage = 20  # This is the known setting

                # Calculate the theoretical max RPM based on the calibration
                theoretical_max_rpm = calibrated_rpm_at_20_percent * (100 // calibrated_percentage)  # 100/20 = 5

                # Calculate the current percentage
                estimated_percentage = min(100, int((avg_rpm / theoretical_max_rpm) * 100))

                # Round to nearest 5 to match typical percentage steps
                estimated_percentage = round(estimated_percentage / 5) * 5
                return min(100, estimated_percentage)
        except Exception as e:
            logger.warning(f'解析传感器数据获取风扇RPM失败: {e}')

        return -1  # Return -1 if unable to determine

    def switch_fan_mode(self, auto: bool):
        """
        switch the fan mode
        :param auto:
        :return:
        """
        manual_cmd = 'raw 0x30 0x30 0x01 0x00'
        auto_cmd = 'raw 0x30 0x30 0x01 0x01'
        return self.run_cmd(cmd=auto_cmd) if auto else self.run_cmd(cmd=manual_cmd)

    def set_fan_speed(self, speed: int):
        """
        set fan speed
        :param speed:
        :return:
        """
        if speed < 10 or speed > 100:
            raise ValueError(
                'speed must be between 10 and 100'
            )

        self.switch_fan_mode(auto=False)
        base_cmd = 'raw 0x30 0x30 0x02 0xff'
        return self.run_cmd(cmd=f'{base_cmd} {hex(speed)}')