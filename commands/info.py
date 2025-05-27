# commands/info.py
from mods.sysinfo import get_sysinfo, fmt_sysinfo


def handle(bot, msg, args):
    sys_info = get_sysinfo()
    formatted_lines = fmt_sysinfo(sys_info)

    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    for line in formatted_lines:
        bot.send_raw(f"PRIVMSG {target} :{line}")