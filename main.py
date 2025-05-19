#!/usr/bin/env python3
import socket
import random
import time
import sys
import os
import re

import mods
import mods.sysinfo

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conf import config_load

# ==============================
# Класс для парсинга префиксов IRC сообщений
# ==============================
class IRCPrefix:
    def __init__(self, raw_prefix: str):
        self.raw = raw_prefix
        self.nick = ""
        self.ident = ""
        self.host = ""

        if "!" in self.raw and "@" in self.raw:
            nick_part, host_part = raw_prefix.split("@", 1)
            nick_ident = nick_part.split("!", 1)
            if len(nick_ident) == 2:
                self.nick = nick_ident[0]
                self.ident = nick_ident[1]
                self.host = host_part
            else:
                self.nick = nick_ident[0]
                self.ident = ""
                self.host = host_part
        elif "!" in self.raw:
            nick_rest = raw_prefix.split("!", 1)
            self.nick = nick_rest[0]
            self.ident = nick_rest[1]
            self.host = ""
        elif "@" in self.raw:
            nick_rest = raw_prefix.split("@", 1)
            self.nick = nick_rest[0]
            self.host = nick_rest[1]
            self.ident = ""
        else:
            self.nick = self.raw
            self.ident = ""
            self.host = ""

# ==============================
# Класс для парсинга IRC сообщений
# ==============================
class IRCMessage:
    def __init__(self, raw_line: str):
        self.raw = raw_line.strip()
        self.prefix = IRCPrefix("")
        self.command = ""
        self.params = []
        self.trailing = ""
        self._parse()

    def _parse(self):
        line = self.raw

        # Парсинг префикса
        prefix_match = re.match(r'^:(\S+) ', line)
        if prefix_match:
            prefix_str = prefix_match.group(1)
            self.prefix = IRCPrefix(prefix_str)
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
            self.trailing = ""

        self.params = params_part.split() if params_part else []

    def __repr__(self):
        return (
            f"<IRCMessage command={self.command} "
            f"prefix={{nick='{self.prefix.nick}', ident='{self.prefix.ident}', host='{self.prefix.host}'}} "
            f"params={self.params} trailing='{self.trailing}'>"
        )

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
def main(config_path):
    auth_nickserv: bool = False
    auth_rusnetns: bool = False

    try:
        cfg = config_load(config_path)
        cfg.print_config()
        print("[+] Configuration loaded successfully.")
    except FileNotFoundError as e:
        print(f"[!] {e}")
        return 1
    except RuntimeError as e:
        print(f"[!] {e}")
        return 1

    if not cfg.acon:
        proceed = input("Продолжить? [Y/n]: ")
        if proceed in ('y', 'Y', ''):
            print("Продолжаем...")
        else:
            print("Завершаем работу.")
            sys.exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((cfg.host, cfg.port))

    #Регистрация
    if cfg.pswd:
        send_raw(sock, "PASS " + cfg.pswd)
        print("[AUTH] Sent PASS command")

    send_raw(sock, "NICK " + cfg.nick)
    send_raw(sock, "USER " + cfg.user + " 0 * :" + cfg.rnam)

    while True:
        try:
            data = sock.recv(4096).decode("utf-8", "ignore")
            if not data:
                print("[!] Lost connection. Reconnecting...")
                time.sleep(5)
                main(config_path)
                return

            lines = data.strip().split("\n")
            for line in lines:
                msg = IRCMessage(line)

                # Отладочный вывод
                print(f"[RAW] {line}")

                # Обработка приветствия сервера RusNet
                if msg.command == '020' and 'rusnet' in msg.trailing.lower():
                        # Сработает на RusNet, rusnet и RUSNET
                        auth_rusnetns: bool = True
                        print("[NOTE] RusNet server detected. ")

                # Обработка ошибки 464 (Password incorrect)
                if msg.command == "464":
                    print("[!] Server rejected the password. Exiting...")
                    return 1 # Выходим с кодом ошибки

                # Обработка PING
                if msg.command == "PING":
                    ping_server = msg.params[0] if msg.params else ""
                    send_raw(sock, f"PONG {ping_server}")

                # Обработка CTCP VERSION
                if msg.command == "PRIVMSG" and msg.trailing.startswith("\x01VERSION\x01"):
                    send_raw(sock, f"NOTICE {msg.prefix.nick} :\x01{cfg.dccv}\x01")
                    print(f"[NOTE] VERSION requested by {msg.prefix.nick}, responding...")

                # Обработка NickName in use
                if msg.command == "433":
                    new_nick = f"{cfg.nick}_{random.randint(1000, 9999)}"
                    send_raw(sock, f"NICK {new_nick}")

                # Обработка MOTD
                if msg.command == "375":
                    print("[+] Connected to the server!")

                # Авторизация через NickServ при получении 376
                if msg.command == "376" or msg.command == "422":
                    if cfg.nspw:
                        if auth_rusnetns:
                            send_raw(sock, f"Nickserv :IDENTIFY {cfg.nspw}")
                            print("[AUTH] Sent RusNet NickServ IDENTIFY command")
                        else:
                            send_raw(sock, f"PRIVMSG Nickserv :IDENTIFY {cfg.nspw}")
                            print("[AUTH] Sent NickServ IDENTIFY command")
                    else:
                        print("[AUTH] No password provided, skipping NickServ auth")
                        
                        for bot_chan in cfg.chan:
                            send_raw(sock, f"JOIN {bot_chan}")
                            print(f"[JOIN] Joining {bot_chan} with unregistered Nickname...")
                            time.sleep(0.5)
                        print("[JOIN] Join command sent to channels...")

                # Проверка успешной авторизации через NickServ
                if msg.command == "NOTICE" and msg.prefix.nick == "NickServ":
                    if any (word in msg.trailing.lower() for word in ["identified", "accepted"]):
                        print("[AUTH] Successfully authenticated with NickServ")
                        for bot_chan in cfg.chan:
                            send_raw(sock, f"JOIN {bot_chan}")
                            print(f"[JOIN] Joining {bot_chan} ...")
                            time.sleep(0.5)
                        print("[JOIN] Join command sent to channels...")


                if msg.command == "PRIVMSG" and msg.trailing.startswith('.'):
                    comm_str = msg.trailing.split()
                    comm = comm_str[0][1:]
                    args = comm_str[1:]
                    print(f"[CMD] Command string: {comm_str}")
                    print(f"[CMD] Command itself: {comm}")
                    print(f"[CMD] Command args  : {args}")
                    # Здесь выполняем команды администраторов             
                    if comm == "join" and msg.prefix.nick in cfg.admi:
                        if len(args) >= 1:
                            for arg in args:
                                send_raw(sock, f"JOIN {arg}")
                                print(f"[JOIN] Joining {arg}")
                                time.sleep(0.5)
                            join_chans = ' '.join(args)
                            send_raw(sock, f"PRIVMSG {msg.params[0]} :Joining {join_chans}")
                            print(f"[+] JOIN {args} sent")
                        else:
                            send_raw(sock, f"PRIVMSG {msg.params[0]} :No args given!")
                            print(f"[!] No args on JOIN command given!")

                    if comm == "part" and msg.prefix.nick in cfg.admi:
                        if len(args) >= 1:
                            for arg in args:
                                send_raw(sock, f"PART {arg}")
                                print(f"[PART] Leaving {arg}")
                                time.sleep(0.5)
                            part_chans = ' '.join(args)
                            send_raw(sock, f"PRIVMSG {msg.params[0]} :Leaving {part_chans}")
                            print(f"[+] PART {args} sent")
                        else:
                            if msg.params[0].startswith('#'):
                                send_raw(sock, f"PART {msg.params[0]} :Leaving current channel!")
                                print(f"[+] PART {msg.params[0]} sent")
                            
                    if comm == "quit" and msg.prefix.nick in cfg.admi:
                        if len(args) >= 1:
                            quit_reason = ' '.join(args)
                            send_raw(sock, f"QUIT :{quit_reason}")
                        else:
                            send_raw(sock, f"QUIT :Bye!")
                        sys.exit()
                    # Здесь выполняем команды для неадминистраторов
                    if comm == "helo":
                        if msg.params[0].startswith('#'):
                            send_raw(sock, f"PRIVMSG {msg.params[0]} :Hello, {msg.prefix.nick}")
                            print(f"[+] HELLO to {msg.params[0]}")
                        else:
                            send_raw(sock, f"PRIVMSG {msg.prefix.nick} :Hello, {msg.prefix.nick}!")
                            print(f"[+] HELLO to {msg.prefix.nick}")

                    if comm == "info":
                        sys_info = mods.sysinfo.get_sysinfo()
                        msg_lines = mods.sysinfo.fmt_sysinfo(sys_info)
                        if msg.params[0].startswith('#'):
                            for line in msg_lines:
                                send_raw(sock, f"PRIVMSG {msg.params[0]} :{line}")
                                print(f"[+] INFO line sent to {msg.params[0]}")
                                time.sleep(0.3)
                        else:
                            for line in msg_lines:
                                send_raw(sock, f"PRIVMSG {msg.prefix.nick} :{line}")
                                print(f"[+] INFO line sent to {msg.prefix.nick}")
                                time.sleep(0.3)
                        print("[+] INFO sent")
                    
        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(5)
            main(config_path)
            return

if __name__ == "__main__":
    # Проверяем, передан ли путь к конфигурации как аргумент
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "./conf/config.toml"

    sys.exit(main(config_file))
