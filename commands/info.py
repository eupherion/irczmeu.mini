# commands/info.py
import time
from datetime import timedelta
from mods.sysinfo import get_sysinfo, fmt_sysinfo


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