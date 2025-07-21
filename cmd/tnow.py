# commands/tnow.py
from datetime import datetime

def handle(bot, msg, args, admin_cmd):
    """
    Shows the current date, time
    """
    time_now = datetime.now()
    time_fmt = time_now.strftime("%A, %B %d, %Y %H:%M:%S")
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    if admin_cmd:
        for admin_nick in bot.config.admi:
            if admin_nick in msg.prefix.nick:
                if not args:
                    bot.send("PRIVMSG", target, f":Time now: {time_fmt}")
    else:
        bot.send("PRIVMSG", target, f":Time is {time_fmt}")