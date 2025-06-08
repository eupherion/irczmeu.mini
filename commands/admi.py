# commands/admi.py
def handle(bot, msg, args, admin_cmd):
    """
    Shows or adds/removes admins: .admi add | del
    """
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    if admin_cmd:
        for admin_nick in bot.config.admi:
            if admin_nick in msg.prefix.nick:
                if not args:
                    bot.send("PRIVMSG", target, f":Admins: {', '.join(bot.config.admi)}")
                elif args[0] == 'add' and len(args) > 1:
                    if args[1] in bot.config.admi:
                        bot.send("PRIVMSG", target, f":{args[1]} is already admin.")
                    else:
                        bot.config.admi.append(args[1])
                        bot.send("PRIVMSG", target, f":Added {args[1]} to admins.")
                elif args[0] == 'del' and len(args) > 1:
                    if args[1] in bot.config.admi:
                        bot.config.admi.remove(args[1])
                        bot.send("PRIVMSG", target, f":Removed {args[1]} from admins.")
                    else:
                        bot.send("PRIVMSG", target, f":{args[1]} is not an admin.")
                else:
                    bot.send("PRIVMSG", target, f":Usage: .admi [add|del] <nick>")
                break
        else:
            bot.send("PRIVMSG", target, f":{msg.pefix.nick}, you are not admin.")
    else:
        bot.send("PRIVMSG", target, f":Admin rights are required for this command.")