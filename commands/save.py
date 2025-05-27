# commands/save.py
def handle(bot, msg, args):
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    cfg_path = bot.config.config_path
    bot.send_raw(f"PRIVMSG {target} :Saving config to {cfg_path}")
    bot.config.save()