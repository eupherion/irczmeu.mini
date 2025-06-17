# commands/info.py
import time
import psutil
import platform
from datetime import timedelta
# from mods.sysinfo import get_sysinfo, fmt_sysinfo


def handle(bot, msg, args, admin_cmd):
    """
    Shows system and uptime information.
    """
    # Цвета
    header_color = "\x0312"   # Светло-синий (для заголовков)
    value_color = "\x0309"    # Светло-зелёный (для значений)
    reset_color = "\x0F"            # Сброс цвета

    sys_info = get_sysinfo()
    formatted_lines = fmt_sysinfo(sys_info)
    time_current = time.time()
    time_passed = time_current - bot.time_connect

    # Используем timedelta для форматирования времени
    time_delta = timedelta(seconds=time_passed)
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_time = f"{days} дней {hours:02}:{minutes:02}:{seconds:02}"

    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    for line in formatted_lines:
        bot.send("PRIVMSG", target, f":{line}")
        time.sleep(0.5)
    
    print(f"[INFO] Online: {formatted_time}")
    bot.send("PRIVMSG", target, f":{header_color}Online  :{reset_color} {value_color}{formatted_time}{reset_color}")

def get_sysinfo():
    # 1. Свободное место на диске (корневая ФС)
    disk = psutil.disk_usage('/')
    disk_info = {
        'total': f"{disk.total / (1024 ** 3):.2f} GB",
        'used': f"{disk.used / (1024 ** 3):.2f} GB",
        'free': f"{disk.free / (1024 ** 3):.2f} GB",
        'percent': f"{disk.percent}%"
    }

    # 2. Использование RAM
    mem = psutil.virtual_memory()
    ram_info = {
        'total': f"{mem.total / (1024 ** 3):.2f} GB",
        'free': f"{mem.available / (1024 ** 3):.2f} GB",
        'used': f"{mem.used / (1024 ** 3):.2f} GB",
        'percent': f"{mem.percent}%"
    }

    # 3. Загрузка CPU (средняя за последнюю минуту)
    cpu_percent = psutil.cpu_percent(interval=1)

    # 4. Температура процессора (можно добавить через psutil.sensors_temperatures(), если доступно)
    if platform.machine() == 'aarch64':  # Например, для Raspberry Pi
        cpu_temp = None
        if psutil.sensors_temperatures():
            for name, entries in psutil.sensors_temperatures().items():
                for entry in entries:
                    if entry.current is not None:
                        cpu_temp = entry.current
    else:
        cpu_temp = None
    

    # 5. Аптайм системы
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

    return {
        'disk': disk_info,
        'ram': ram_info,
        'cpu': f"{cpu_percent}%",
        'cpu_temp': f"{cpu_temp}°C" if cpu_temp is not None else "N/A",
        'uptime': f"{int(uptime_seconds // 86400)} дней {uptime_str}"
    }

def fmt_sysinfo(info):
    # Цвета
    header_color = "\x0312"   # Светло-синий (для заголовков)
    value_color = "\x0309"    # Светло-зелёный (для значений)
    reset_color = "\x0F"            # Сброс цвета

    # Форматируем SSD
    ssd = info['disk']
    ssd_line = f"{header_color}SSD [GB]:{reset_color} {value_color}{ssd['used']}({ssd['percent']})/{ssd['free']}/{ssd['total']}{reset_color}"

    # Форматируем RAM
    ram = info['ram']
    ram_line = f"{header_color}RAM [GB]:{reset_color} {value_color}{ram['used']}({ram['percent']})/{ram['free']}/{ram['total']}{reset_color}"

    # CPU и аптайм — простое форматирование
    cpu_line = f"{header_color}CPU [N%]:{reset_color} {value_color}{info['cpu']}{reset_color}"
    cpu_temp_line = f"{header_color}CPU Temp:{reset_color} {value_color}{info['cpu_temp']}{reset_color}"
    uptime_line = f"{header_color}Uptime  :{reset_color} {value_color}{info['uptime']}{reset_color}"

    # Объединяем всё в список строк
    return [ssd_line, ram_line, cpu_line, cpu_temp_line, uptime_line]