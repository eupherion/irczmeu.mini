# commands/part.py
import time
def handle(bot, msg, args, admin_cmd):
    """
    Part channels: .part <#channel> [<#channel> ...]
    """
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    chans = ' '.join(args)
    if admin_cmd:
        if not args:
            bot.send("PRIVMSG", target, f":Usage: part <#channel> [<#channel> ...]")
        else:
            for admin_nick in bot.config.admi:
                if admin_nick in msg.prefix.nick:
                    bot.send("PRIVMSG", target, f":Part {chans}")
                    for arg in args:
                        bot.send("PART", arg)
                        time.sleep(0.5)
                break
            else:
                bot.send("PRIVMSG", target, f":You are not an admin")
                return
    else:
        bot.send("PRIVMSG", target, f":Part {chans}")
        for arg in args:
            bot.send("PART", arg)
            time.sleep(0.5)
        return
    
    

    