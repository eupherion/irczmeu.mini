def handle(bot, msg, args, admin_cmd):
    """
    Reconnect the bot to the IRC network.
    """
    reason = ' '.join(args)
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    if bot.config.acon is True and admin_cmd:
        for admin_nick in bot.config.admi:
            if admin_nick in msg.prefix.nick:
                if reason:
                    bot.send("PRIVMSG", target, f":{msg.prefix.nick} Reconnecting: {reason}")
                else:
                    bot.send("PRIVMSG", target, f":{msg.prefix.nick} Reconnecting")
                bot.reconnect()
                break
        else:
            bot.send("PRIVMSG", target, f":{msg.prefix.nick} You are not an admin!")
            return
    else:
        if not bot.config.acon:
            bot.send("PRIVMSG", target, f":Bot is not cofigured for autoreconnect!")
        if not admin_cmd:
            bot.send("PRIVMSG", target, f":Seems you are not admin! Sorry...")
