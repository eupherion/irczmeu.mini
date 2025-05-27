# commands/quit.py
def handle(bot, msg, args):
    reason = ' '.join(args) if args else "Bye!"
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    bot.send_raw(f"PRIVMSG {target} : {msg.prefix.nick} I'm quitting: {reason}")
    bot.send_raw(f"QUIT :{reason}")
    bot.exit(0, reason)