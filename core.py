# bot.py
import socket
import random
import atexit
import time
import sys
import re
import os
import importlib.util

from conf import config_load

# ==============================
# Класс для парсинга префиксов IRC сообщений
# ==============================
class IRCPrefix:
    def __init__(self, raw_prefix: str):
        self.raw = raw_prefix # Полный префикс IRC сообщения
        self.nick = "" # Ник отправителя IRC сообщения  
        self.ident = "" # Идентификатор отправителя IRC сообщения
        self.host = "" # Хост отправителя IRC сообщения

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
        self.raw: str = raw_line.strip() # Строка с полным сообщением
        self.prefix = IRCPrefix("") # Префикс сообщения
        self.command = "" # Команда IRC сообщения (например PRIVMSG)
        self.params = [] # Параметры IRC сообщения (например список каналов)
        self.trailing = "" # Трейлинг IRC сообщения (например сообщение)
        self._parse() # Парсинг сообщения

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

class Bot:
    def __init__(self, config_path):
        self.config = config_load(config_path)
        self.sock = None
        self.commands_dir = "commands"
        self.loaded_commands = {}
        self.command_descriptions = {}  # <-- новый словарь для описаний
        self.auth_rusnetns = False
        self.time_connect = 0.0
        # Регистрируем выход из программы при завершении
        atexit.register(self.on_exit)

    def exit(self, code=0, reason=""):
        if reason:
            print(f"[INFO] Exiting with reason: {reason}")
        sys.exit(code)

    def on_exit(self):
        print("[INFO] Saving configuration before exit...")
        self.config.save()

    def load_commands(self):
        if not os.path.exists(self.commands_dir):
            print(f"[!] Commands directory '{self.commands_dir}' not found.")
            return

        for filename in os.listdir(self.commands_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module_path = os.path.join(self.commands_dir, filename)

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None:
                    print(f"[!] Failed to load module spec for {module_name}")
                    continue

                if spec.loader is None:
                    print(f"[!] Module {module_name} has no loader")
                    continue

                module = importlib.util.module_from_spec(spec)

                try:
                    spec.loader.exec_module(module)
                except Exception as e:
                    print(f"[!] Error executing module {module_name}: {e}")
                    continue

                if hasattr(module, "handle"):
                    command_name = module_name.lower()
                    self.loaded_commands[command_name] = module.handle

                    # Читаем docstring у handle
                    description = module.handle.__doc__
                    self.command_descriptions[command_name] = description.strip() if description else "No description available"

                    print(f"[+] Loaded command: .{command_name}")
                else:
                    print(f"[!] Module {module_name} has no 'handle' function. Skipping.")

    # def handle_command(self, msg):
    #     """Обработка команды"""
    #     if not msg.trailing.startswith(self.config.csym):
    #         return

    #     raw_command = msg.trailing[len(self.config.csym):]
    #     parts = raw_command.split(" ", 1)
    #     cmd_name = parts[0].lower()
    #     args = parts[1].split() if len(parts) > 1 else []

    #     handler = self.loaded_commands.get(cmd_name)
    #     if handler:
    #         try:
    #             handler(self, msg, args, admin_cmd = True)
    #         except Exception as e:
    #             print(f"[!] Error executing command .{cmd_name}: {e}")
    #     else:
    #         print(f"[CMD] Unknown command: .{cmd_name}")

    def handle_command(self, msg):
        """Обработка команды"""
        if not msg.trailing.startswith(self.config.csym):
            return

        raw_command = msg.trailing[len(self.config.csym):]
        parts = raw_command.split(" ", 1)
        cmd_name = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []

        # Обработка .help
        if cmd_name == "help":
            help_title = "Available commands:"
            target = msg.params[0] if msg.params[0] != self.config.nick else msg.prefix.nick
            self.send("PRIVMSG", target, f":{help_title}")
            # Перечисляем команды и отправляем пользователю
            for name in sorted(self.loaded_commands.keys()):
                desc = self.command_descriptions.get(name, "No description available")
                self.send("PRIVMSG", target, f":{self.config.csym}{name} - {desc}")
                
            print(f"[HELP] Sent help to {target}")
            return

        # Обработка обычных команд
        handler = self.loaded_commands.get(cmd_name)
        if handler:
            try:
                handler(self, msg, args, admin_cmd=True)
            except Exception as e:
                print(f"[!] Error executing command .{cmd_name}: {e}")
        else:
            print(f"[CMD] Unknown command: .{cmd_name}")

    def connect(self):
        """Подключение к серверу"""
        print("[+] Loading configuration...")
        self.config.print_config()
        if not self.config.acon:
            proceed = input("Continue? [Y/n]: ")
            if proceed not in ('y', 'Y', ''):
                print("Exiting.")
                sys.exit(0)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.config.host, self.config.port))
            print(f"[+] Connected to {self.config.host}:{self.config.port}")
            self.time_connect = time.time()
        except Exception as e:
            print(f"[!] Connection error: {e}")
            sys.exit(1)

    def send_raw(self, message):
        if self.sock is None:
            print("[!] Cannot send message: socket is not connected.")
            return
        # Отправка сообщения с префиксом и переводом строки
        print(f">>> {message}")
        self.sock.sendall((message + "\r\n").encode('utf-8'))

    def send(self, command, *params):
        """
        Отправляет IRC-команду через сокет.
        Пример: bot.send("PRIVMSG", "#channel", ":Hello world")
        """
        trailing = ""
        if params and params[-1].startswith(":"):
            trailing = params[-1]
            params = params[:-1]

        if trailing:
            line = f"{command} {' '.join(params)} {trailing}"
        else:
            line = f"{command} {' '.join(params)}"
        try:
            if self.sock is None:
                print(f"[!] Cannot send message [{line}] : socket is not connected.")
                return
            print(f">>> {line}")
            self.sock.sendall((line + "\r\n").encode("utf-8"))
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")

    def register(self):
        """Регистрация бота на сервере"""
        if self.config.pswd:
            self.send_raw("PASS " + self.config.pswd)
        self.send_raw(f"NICK {self.config.nick}")
        self.send_raw(f"USER {self.config.user} 0 * :{self.config.rnam}")

    def reconnect(self):
        """Переподключение"""
        print("[!] Lost connection. Reconnecting...")
        time.sleep(5)
        if self.sock is None:
            print("[!] Cannot disconnect: socket is not connected.")
            return
        self.sock.close()
        self.connect()
        self.register()

    def run(self):
        """Основной цикл работы бота"""
        self.connect()
        self.register()
        self.load_commands()

        while True:
            try:
                if self.sock is None:
                    print("[!] Cannot receive message: socket is not connected.")
                    self.reconnect()
                    continue
                    
                data = self.sock.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    self.reconnect()
                    continue

                lines = data.strip().split("\r\n")
                for line in lines:
                    msg = IRCMessage(line)

                    # Debug output
                    print(f"[RAW] {line}")

                    # PING/PONG
                    if msg.command == "PING":
                        ping_server = msg.params[0] if msg.params else ""
                        self.send_raw(f"PONG {ping_server}")

                    # RusNet server detection
                    if msg.command == '020' and 'rusnet' in msg.trailing.lower():
                        self.auth_rusnetns: bool = True
                        print("[NOTE] RusNet server detected. ")

                    # CTCP VERSION
                    if msg.command == "PRIVMSG" and msg.trailing.startswith("\x01VERSION\x01"):
                        self.send_raw(f"NOTICE {msg.prefix.nick} :\x01{self.config.dccv}\x01")

                    # Nickname in use
                    if msg.command == "433":
                        new_nick = f"{self.config.nick}_{random.randint(1000, 9999)}"
                        self.send_raw(f"NICK {new_nick}")

                    # MOTD finish
                    if msg.command == "375":
                        print("[+] Connected to the server!")

                    # Auth via NickServ
                    if msg.command in ("376", "422"):
                        if self.config.nspw:
                            if self.auth_rusnetns:
                                self.send_raw(f"Nickserv :IDENTIFY {self.config.nspw}")
                            else:
                                self.send_raw(f"PRIVMSG Nickserv :IDENTIFY {self.config.nspw}")
                        else:
                            for chan in self.config.chan:
                                self.send_raw(f"JOIN {chan}")

                    # Success auth
                    if msg.command == "NOTICE" and msg.prefix.nick == "NickServ":
                        if any(word in msg.trailing.lower() for word in ["identified", "accepted"]):
                            for chan in self.config.chan:
                                self.send_raw(f"JOIN {chan}")

                    # Command handling
                    if msg.command == "PRIVMSG":
                        self.handle_command(msg)

            except KeyboardInterrupt:
                print("\n[INFO] Shutting down gracefully...")
                if self.sock is not None:
                    self.sock.close()
                sys.exit(0)

            except Exception as e:
                print(f"[ERROR] Critical error: {e}")
                if self.sock is not None:
                    self.sock.close()
                sys.exit(1)

    def __del__(self):
        """Закрытие соединения при завершении работы"""
        if self.sock is not None:
            self.sock.close()
            