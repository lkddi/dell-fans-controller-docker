import subprocess
import time
import re
from controller.logger import logger


# IPMI命令封装器：负责调用ipmitool读取传感器并设置Dell风扇
class IpmiTool:
    # 初始化iDRAC连接参数
    def __init__(self, host: str, username: str, password: str):
        if not host or not username or not password:
            raise ValueError("host, username and password must be provided")
        self.host = host
        self.username = username
        self.password = password

    # 执行ipmitool命令并处理重试、超时和会话异常
    def run_cmd(self, cmd: str) -> str:
        basecmd = f'ipmitool -H {self.host} -I lanplus -U {self.username} -P {self.password}'
        command = f'{basecmd} {cmd}'
        retry_count = 5  # 增加重试次数以应对网络波动
        for attempt in range(retry_count):
            try:
                # print(f"Executing command: {command}")  # 添加调试信息
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)  # 增加超时时间

                if result.returncode != 0:
                    # 部分ipmitool版本会把错误输出到stdout，或只返回退出码但stderr为空
                    error_msg = result.stderr.strip() or result.stdout.strip() or f'命令退出码: {result.returncode}'
                    # 检查是否是网络连接问题
                    if "Unable to establish IPMI" in error_msg or "session" in error_msg:
                        logger.warning(f'IPMI会话建立失败 (尝试 {attempt + 1}/{retry_count}): {error_msg}')
                        if attempt < retry_count - 1:
                            time.sleep(10)  # 网络问题需要更长的等待时间
                            continue
                    raise RuntimeError(
                        f'IPMI 命令执行失败: {cmd}\n错误详情: {error_msg}'  # 更清晰的错误提示
                    )

                return result.stdout
            except subprocess.TimeoutExpired:
                logger.warning(f'命令超时 (尝试 {attempt + 1}/{retry_count})')
                if attempt < retry_count - 1:
                    logger.warning(f'正在重试... (尝试次数 {attempt + 1}/{retry_count})')
                    time.sleep(10)  # 每次重试前等待更长时间
                else:
                    raise RuntimeError('IPMI 命令超时。请检查网络连接或服务器状态。')  # 更明确的错误提示
            except Exception as e:
                logger.warning(f'IPMI命令执行异常 (尝试 {attempt + 1}/{retry_count}): {str(e)}')
                if attempt < retry_count - 1:
                    time.sleep(10)  # 网络问题需要更长的等待时间
                else:
                    raise e

    # 读取iDRAC控制器基本信息
    def mc_info(self) -> str:
        """
        执行ipmitool mc info命令
        :return:
        """
        return self.run_cmd(cmd='mc info')

    # 读取完整SDR传感器数据
    def sensor(self) -> str:
        """
        执行ipmitool sdr命令获取传感器数据
        :return:
        """
        return self.run_cmd(cmd='sdr')

    # 从SDR数据中解析温度传感器列表
    def temperature(self, data: str = None) -> list:
        """
        获取当前温度传感器列表
        :return:
        """
        if data is None:
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

    # 从SDR数据中解析风扇RPM列表
    def fan_speeds(self) -> list:
        """
        获取当前风扇RPM列表
        :return: 风扇RPM列表
        """
        data = self.sensor()
        fan_speeds = []

        for line in data.splitlines():
            if 'Fan' in line and 'RPM' in line:
                # 从传感器行中提取RPM数值，典型格式为 "Fan1 RPM | 4800 RPM | ok"
                parts = line.split('|')
                if len(parts) >= 2:
                    try:
                        value_str = parts[1].strip()
                        if value_str.isdigit():
                            rpm = int(value_str)
                            fan_speeds.append(rpm)
                    except ValueError:
                        continue
        return fan_speeds

    # 获取当前风扇占空比，raw命令不可用时用RPM估算
    def get_fan_duty_cycle(self, sensor_data: str = None) -> int:
        """
        获取当前风扇占空比/百分比
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
            data = sensor_data if sensor_data is not None else self.sensor()
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

    # 切换风扇自动/手动模式
    def switch_fan_mode(self, auto: bool):
        """
        切换风扇模式
        :param auto:
        :return:
        """
        manual_cmd = 'raw 0x30 0x30 0x01 0x00'
        auto_cmd = 'raw 0x30 0x30 0x01 0x01'
        return self.run_cmd(cmd=auto_cmd) if auto else self.run_cmd(cmd=manual_cmd)

    # 设置手动风扇速度百分比
    def set_fan_speed(self, speed: int):
        """
        设置风扇速度
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
