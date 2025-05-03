#!/usr/bin/env python3
import socket
import random
import toml
import time
import sys
import os
import re

class Config:
    def __init__(self, config_dict):
        self.host = config_dict.get("ircServer", {}).get("ircServerHost")
        self.port = config_dict.get("ircServer", {}).get("ircServerPort")
        self.pswd = config_dict.get("ircServer", {}).get("ircServerPass")

        self.user = config_dict.get("ircClient", {}).get("ircBotUser")
        self.nick = config_dict.get("ircClient", {}).get("ircBotNick")
        self.rnam = config_dict.get("ircClient", {}).get("ircBotRnam")
        self.nspw = config_dict.get("ircClient", {}).get("ircBotNspw")
        self.chan = config_dict.get("ircClient", {}).get("ircBotChan")
        self.admi = config_dict.get("ircClient", {}).get("ircBotAdmi")
        self.acon = config_dict.get("ircClient", {}).get("ircBotAcon")
        self.csym = config_dict.get("ircClient", {}).get("ircBotCsym")
        self.rcon = config_dict.get("ircClient", {}).get("ircBotRcon")
        self.dccv = config_dict.get("ircClient", {}).get("ircBotDccv")

    def print_config(self):
        # Максимальная длина строки до двоеточия
        max_key_length = max(
            len("Host"),
            len("Port"),
            len("Password"),
            len("User"),
            len("Nickname"),
            len("Real Name"),
            len("Nickserv Password"),
            len("Channel"),
            len("Admin"),
            len("Auto Connect"),
            len("Command Symbol"),
            len("Reconnect"),
            len("DCC Version")
        )

        print("=== IRC Server Configuration ===")
        print(f"{'Host':<{max_key_length}}: {self.host}")
        print(f"{'Port':<{max_key_length}}: {self.port}")
        print(f"{'Password':<{max_key_length}}: {self.pswd}")

        print("\n=== IRC Client Configuration ===")
        print(f"{'User':<{max_key_length}}: {self.user}")
        print(f"{'Nickname':<{max_key_length}}: {self.nick}")
        print(f"{'Real Name':<{max_key_length}}: {self.rnam}")
        print(f"{'Nickserv Password':<{max_key_length}}: {self.nspw}")
        print(f"{'Channel':<{max_key_length}}: {self.chan}")
        print(f"{'Admin':<{max_key_length}}: {self.admi}")
        print(f"{'Auto Connect':<{max_key_length}}: {self.acon}")
        print(f"{'Command Symbol':<{max_key_length}}: {self.csym}")
        print(f"{'Reconnect':<{max_key_length}}: {self.rcon}")
        print(f"{'DCC Version':<{max_key_length}}: {self.dccv}")

# ==============================
# Класс для парсинга IRC сообщений
# ==============================
class IRCMessage:
    def __init__(self, raw_line: str):
        self.raw = raw_line.strip()
        self.prefix = None
        self.command = None
        self.params = []
        self.trailing = None
        self._parse()

    def _parse(self):
        line = self.raw

        # Извлечение префикса (если есть)
        prefix_match = re.match(r'^:(\S+) ', line)
        if prefix_match:
            self.prefix = prefix_match.group(1)
            line = line[len(prefix_match.group(0)):]

        # Команда — первое слово
        parts = line.split(" ", 1)
        self.command = parts[0]

        rest = parts[1] if len(parts) > 1 else ""

        # Разделение параметров и trailing
        if " :" in rest:
            params_part, trailing_part = rest.split(" :", 1)
            self.trailing = trailing_part
        else:
            params_part = rest

        if params_part:
            self.params = params_part.split()

    def __repr__(self):
        return f"<IRCMessage command={self.command} prefix={self.prefix} params={self.params} trailing={self.trailing}>"

def enc_bytes(s):
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s.encode("utf-8")

# ==============================
# Функция отправки команды серверу
# ==============================
def send_raw(s, message):
    print(f">>> {message}")
    s.sendall((message + "\r\n").encode('utf-8'))


# ==============================
# Основной цикл работы бота
# ==============================
def main(config_path="config.toml"):
    auth_nickserv = False
    auth_rusnetns = False
    # Проверяем существование файла
    if not os.path.exists(config_path):
        print(f"[!] Configuration file '{config_path}' not found.")
        return 1 # Выходим с кодом ошибки
    
    #Читаем файл конфигурации
    try:
        with open(config_path, "r") as file:
            config_data = toml.load(file)
        print("[+] Configuration file loaded successfully.")
        bot = Config(config_data)
        bot.print_config()
    except Exception as e:
        print(f"[!] Error reading configuration file: {e}")
        return 1 # Выходим с кодом ошибки

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((bot.host, bot.port))

    #Регистрация
    send_raw(sock, "NICK " + bot.nick)
    send_raw(sock, "USER " + bot.user + " 0 * :" + bot.rnam)

    while True:
        try:
            data = sock.recv(4096).decode("utf-8", "ignore")
            if not data:
                print("[!] Lost connection. Reconnecting...")
                time.sleep(5)
                main()
                return

            lines = data.strip().split("\n")
            for line in lines:
                msg = IRCMessage(line)

                # Отладочный вывод
                print(f"[RAW] {line}")

                # Обработка приветствия сервера RusNet
                if msg.command == '020' and 'RusNet' in msg.trailing:
                    auth_rusnetns = True
                    print("[NOTE] RusNet server detected.")

                # Обработка PING
                if msg.command == "PING":
                    ping_server = msg.params[0] if msg.params else ""
                    send_raw(sock, f"PONG {ping_server}")

                # Обработка CTCP VERSION
                if msg.command == "PRIVMSG" and msg.trailing and msg.trailing.startswith("\x01VERSION\x01"):
                    user_nick = msg.prefix.split("!")[0]
                    send_raw(sock, f"NOTICE {user_nick} :\x01VERSION MyBot/1.0 Python\x01")

                # Обработка NickName in use
                if msg.command == "433":
                    new_nick = f"{bot.nick}_{random.randint(1000, 9999)}"
                    send_raw(sock, f"NICK {new_nick}")

                # Обработка MOTD
                if msg.command == "375":
                    print("[+] Connected to the server!")

                # Авторизация через NickServ при получении 376
                if msg.command == "376":
                    if bot.nspw:
                        if auth_rusnetns:
                            send_raw(sock, f"Nickserv :IDENTIFY {bot.nspw}")
                            print("[AUTH] Sent RusNet NickServ IDENTIFY command")
                        else:
                            send_raw(sock, f"PRIVMSG Nickserv :IDENTIFY {bot.nspw}")
                            print("[AUTH] Sent NickServ IDENTIFY command")
                    else:
                        print("[AUTH] No password provided, skipping NickServ auth")
                        send_raw(sock, f"JOIN {bot.chan}")
                        print("[JOIN] Joining the channel...")

                # Проверка успешной авторизации через NickServ
                if (msg.command == "NOTICE" and
                    msg.prefix.startswith("NickServ!") and
                    any(word in msg.trailing.lower() for word in ["identified", "accepted"])):
                    auth_nickserv = True
                    print("[AUTH] Successfully authenticated with NickServ")
                    print("[JOIN] Joining the channel...")
                    send_raw(sock, f"JOIN {bot.chan}")
                
        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(5)
            main()
            return

if __name__ == "__main__":
    # Проверяем, передан ли путь к конфигурации как аргумент
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.toml"

    sys.exit(main(config_file))
    main()
