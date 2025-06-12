# commands/info.py
import time
import psutil
from datetime import timedelta
# from mods.sysinfo import get_sysinfo, fmt_sysinfo


def handle(bot, msg, args, admin_cmd):
    """
    Shows system and uptime information.
    """
    # Цвета
    HEADER_COLOR = "\x0312"   # Светло-синий (для заголовков)
    VALUE_COLOR = "\x0309"    # Светло-зелёный (для значений)
    RESET = "\x0F"            # Сброс цвета

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
    bot.send("PRIVMSG", target, f":{HEADER_COLOR}Online  :{RESET} {VALUE_COLOR}{formatted_time}{RESET}")

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

    # 4. Аптайм системы
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

    return {
        'disk': disk_info,
        'ram': ram_info,
        'cpu': f"{cpu_percent}%",
        'uptime': f"{int(uptime_seconds // 86400)} дней {uptime_str}"
    }

def fmt_sysinfo(info):
    # Цвета
    HEADER_COLOR = "\x0312"   # Светло-синий (для заголовков)
    VALUE_COLOR = "\x0309"    # Светло-зелёный (для значений)
    RESET = "\x0F"            # Сброс цвета

    # Форматируем SSD
    ssd = info['disk']
    ssd_line = f"{HEADER_COLOR}SSD [GB]:{RESET} {VALUE_COLOR}{ssd['used']}({ssd['percent']})/{ssd['free']}/{ssd['total']}{RESET}"

    # Форматируем RAM
    ram = info['ram']
    ram_line = f"{HEADER_COLOR}RAM [GB]:{RESET} {VALUE_COLOR}{ram['used']}({ram['percent']})/{ram['free']}/{ram['total']}{RESET}"

    # CPU и аптайм — простое форматирование
    cpu_line = f"{HEADER_COLOR}CPU [N%]:{RESET} {VALUE_COLOR}{info['cpu']}{RESET}"
    uptime_line = f"{HEADER_COLOR}Uptime  :{RESET} {VALUE_COLOR}{info['uptime']}{RESET}"

    # Объединяем всё в список строк
    return [ssd_line, ram_line, cpu_line, uptime_line]