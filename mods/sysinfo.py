import os
from shlex import join
import time

def read_cpu_usage():
    with open("/proc/stat") as f:
        line = f.readline()
    parts = list(map(int, line.split()[1:]))
    total = sum(parts)
    idle = parts[3]
    return total, idle

def get_uptime():
    with open("/proc/uptime") as f:
        uptime_seconds = float(f.readline().split()[0])
    return time.strftime("%H:%M:%S", time.gmtime(uptime_seconds)), int(uptime_seconds // 86400)

def get_sysinfo():
    # 1. Свободное место на диске
    st = os.statvfs("/")
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize

    # 2. RAM
    with open("/proc/meminfo") as f:
        meminfo = f.readlines()
    mem_total = int(meminfo[0].split()[1]) * 1024
    mem_free = int(meminfo[1].split()[1]) * 1024
    mem_available = int(meminfo[2].split()[1]) * 1024
    mem_used = mem_total - mem_free

    # 3. CPU загрузка
    t1, i1 = read_cpu_usage()
    time.sleep(0.1)
    t2, i2 = read_cpu_usage()
    cpu_usage = 100 * ((t2 - t1) - (i2 - i1)) / (t2 - t1)

    # 4. Аптайм
    uptime_str, uptime_days = get_uptime()

    return {
        'ssd [GB]': {
            'used': f"{used / (1024 ** 3):.2f}",
            'free': f"{free / (1024 ** 3):.2f}",
            'total': f"{total / (1024 ** 3):.2f}",
        },
        'ram [GB]': {
            'used': f"{mem_used / (1024 ** 3):.2f}",
            'free': f"{mem_free / (1024 ** 3):.2f}",
            'total': f"{mem_total / (1024 ** 3):.2f}",               
        },
        'cpu': f"{cpu_usage:.1f}%",
        'uptime': f"{uptime_days} дней {uptime_str}"
    }

def fmt_sysinfo(info):
    # Цвета
    HEADER_COLOR = "\x0312"   # Светло-синий (для заголовков)
    VALUE_COLOR = "\x0309"     # Светло-зелёный (для значений)
    RESET = "\x0F"             # Сброс цвета

    # Форматируем SSD
    ssd = info['ssd [GB]']
    ssd_line = f"{HEADER_COLOR}SSD [GB]:{RESET} {VALUE_COLOR}{ssd['used']}/{ssd['free']}/{ssd['total']}{RESET}"

    # Форматируем RAM
    ram = info['ram [GB]']
    ram_line = f"{HEADER_COLOR}RAM [GB]:{RESET} {VALUE_COLOR}{ram['used']}/{ram['free']}/{ram['total']}{RESET}"

    # CPU и аптайм — простое форматирование
    cpu_line = f"{HEADER_COLOR}CPU [N%]:{RESET} {VALUE_COLOR}{info['cpu']}{RESET}"
    uptime_line = f"{HEADER_COLOR}SystemUp:{RESET} {VALUE_COLOR}{info['uptime']}{RESET}"

    # Объединяем всё в список строк
    return [ssd_line, ram_line, cpu_line, uptime_line]

# Пример использования
# if __name__ == "__main__":
#     sys_info = get_sysinfo()
#     formatted_lines = fmt_sysinfo(sys_info)
#     for line in formatted_lines:
#         print(line)