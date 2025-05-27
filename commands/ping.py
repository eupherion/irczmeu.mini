import platform
import subprocess
import re
from ping3 import ping

def handle(bot, msg, args):
    target = msg.params[0] if msg.params[0].startswith('#') else msg.prefix.nick
    if args:
        res_host = args[0]
    else:
        res_host = bot.config.host

    # Определяем операционную систему
    os_name = platform.system()

    if os_name == "Windows":
        # Для Windows используем ping3
        res_time = ping(res_host)
        if res_time is not None:
            bot.send_raw(f"PRIVMSG {target} :{msg.prefix.nick}, Ping reply from {res_host} is {res_time * 1000:.2f} ms")
        else:
            bot.send_raw(f"PRIVMSG {target} :{msg.prefix.nick}, таймаут или ошибка.")
    
    elif os_name in ("Linux", "Darwin"):
        # Для Linux/macOS используем системную команду ping
        try:
            # Формируем команду в зависимости от ОС
            command = ['ping', '-c', '1', '-W', '2', res_host] if os_name == "Linux" else ['ping', '-c', '1', res_host]
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                bot.send_raw(f"PRIVMSG {target} :{msg.prefix.nick}, Ping {res_host}: таймаут или ошибка.")
                return
            
            # Парсим вывод команды
            output = result.stdout
            match = re.search(r"time=(\d+\.?\d*)", output)
            if match:
                res_time = float(match.group(1))
                bot.send_raw(f"PRIVMSG {target} :{msg.prefix.nick}, Ping reply from {res_host} is {res_time:.2f} ms")
            else:
                bot.send_raw(f"PRIVMSG {target} :{msg.prefix.nick}, не удалось получить время ответа от {res_host}.")
        
        except Exception as e:
            bot.send_raw(f"PRIVMSG {target} :{msg.prefix.nick}, ошибка выполнения команды: {str(e)}")
    
    else:
        bot.send_raw(f"PRIVMSG {target} :{msg.prefix.nick}, неизвестная операционная система.")