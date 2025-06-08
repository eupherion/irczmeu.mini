# commands/join.py
import time

def chan_name(chan):
    """Проверяет, является ли имя канала валидным по стандартам IRC."""
    valid_prefixes = ("#", "&", "+", "!")
    if not chan.startswith(valid_prefixes):
        return False, f"Channel starts with {valid_prefixes}"
    if len(chan) > 200:
        return False, "Channel name too long (>200)"
    return True, ""

def handle(bot, msg, args, admin_cmd):
    """
    Join channels: .join <#channel> [<#channel> ...]
    """
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    chans = ' '.join(args)
    if admin_cmd:
        if not args:
            bot.send("PRIVMSG", target, f':Usage: join <#channel> [<#channel> ...]')
        else:
            for admin_nick in bot.config.admi:
                if admin_nick in msg.prefix.nick:
                    bot.send("PRIVMSG", target, f":Joining {chans}")
                    for arg in args:
                        chan_valid, reason = chan_name(arg)
                        if not chan_valid:
                            bot.send("PRIVMSG", target, f":Invalid channel '{arg}': {reason}")
                            continue
                        bot.send("JOIN", arg)
                        time.sleep(1)
                break
            else:
                bot.send("PRIVMSG", target, f":{msg.prefix.nick}, you are not an admin.")
                return
    else:
        bot.send("PRIVMSG", target, f":Joining {chans}")
        for arg in args:
            chan_valid, reason = chan_name(arg)
            if not chan_valid:
                bot.send("PRIVMSG", target, f":Invalid channel '{arg}': {reason}")
                continue
            bot.send("JOIN", arg)
            time.sleep(1)
        return
    