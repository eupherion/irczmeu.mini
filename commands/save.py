# commands/save.py
def handle(bot, msg, args, admin_cmd):
    """
    Save the current configuration to a file.
    """
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    if args:
        cfg_path = "./botconfigs/" + args[0]
    else:
        cfg_path = bot.config.config_path
    if admin_cmd:
        for admin_nick in bot.config.admi:
            if admin_nick in msg.prefix.nick:
                bot.send("PRIVMSG", target, f":Saving config to {cfg_path}")
                bot.config.save(cfg_path)
                print(f"[CONF]Saved config to {cfg_path}")
                break
        else:
            bot.send("PRIVMSG", target, f":You are not an admin!")
            return
    else:
        bot.send("PRIVMSG", target, f":Saving config to {cfg_path}")
        bot.config.save(cfg_path)
        print(f"[CONF]Saved config to {cfg_path}")
        return
