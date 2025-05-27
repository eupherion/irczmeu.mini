# commands/join.py
def handle(bot, msg, args):
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    chans = ' '.join(args)
    bot.send_raw(f"PRIVMSG {target} :Joining {chans}")
    for arg in args:
        bot.send_raw(f"JOIN {arg}")