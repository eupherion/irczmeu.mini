def handle(bot, msg, args):
    reason = ' '.join(args)
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    if bot.config.acon is True:
        if reason:
            bot.send_raw(f"PRIVMSG {target} :Reconnecting: ({reason})")
        else:
            bot.send_raw(f"PRIVMSG {target} :Reconnecting...")
        bot.reconnect()
    else:
        bot.send_raw(f"NOTICE {target} : Autoconnect is not set to true!")
    