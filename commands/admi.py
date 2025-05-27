# commands/admi.py
def handle(bot, msg, args):
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    if not args:
        bot.send_raw(f"PRIVMSG {target} :Admins: {', '.join(bot.config.admi)}")
    elif args[0] == 'add' and len(args) > 1:
        if args[1] in bot.config.admi:
            bot.send_raw(f"PRIVMSG {target} :{args[1]} is already admin.")
        else:
            bot.config.admi.append(args[1])
            bot.send_raw(f"PRIVMSG {target} :Added {args[1]} to admins.")
    elif args[0] == 'del' and len(args) > 1:
        if args[1] in bot.config.admi:
            bot.config.admi.remove(args[1])
            bot.send_raw(f"PRIVMSG {target} :Removed {args[1]} from admins.")
        else:
            bot.send_raw(f"PRIVMSG {target} :{args[1]} is not an admin.")
    else:
        bot.send_raw(f"PRIVMSG {target} :Usage: .admi [add|del] <nick>")