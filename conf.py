#!/usr/bin/env python3
import toml
import os

class Config:
    def __init__(self, config_dict):
        self.host = config_dict.get("ircServer", {}).get("ircServerHost")
        self.port = config_dict.get("ircServer", {}).get("ircServerPort")
        self.pswd = config_dict.get("ircServer", {}).get("ircServerPass")

        self.user = config_dict.get("ircClient", {}).get("ircBotUser")
        self.nick = config_dict.get("ircClient", {}).get("ircBotNick")
        self.rnam = config_dict.get("ircClient", {}).get("ircBotRnam")
        self.nspw = config_dict.get("ircClient", {}).get("ircBotNspw")       
        self.acon = config_dict.get("ircClient", {}).get("ircBotAcon")
        self.csym = config_dict.get("ircClient", {}).get("ircBotCsym")
        self.rcon = config_dict.get("ircClient", {}).get("ircBotRcon")
        self.dccv = config_dict.get("ircClient", {}).get("ircBotDccv")
        self.chan = config_dict.get("ircClient", {}).get("ircBotChan", [])
        self.admi = config_dict.get("ircClient", {}).get("ircBotAdmi", [])

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
            len("Auto Connect"),
            len("Command Symbol"),
            len("Run on connsect"),
            len("DCC Version"),
            len("Channels"),
            len("Admins"),
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
        print(f"{'Auto Connect':<{max_key_length}}: {self.acon}")
        print(f"{'Command Symbol':<{max_key_length}}: {self.csym}")
        print(f"{'Run on connect':<{max_key_length}}: {self.rcon}")
        print(f"{'DCC Version':<{max_key_length}}: {self.dccv}")
        print(f"{'Channels':<{max_key_length}}: {self.chan}")
        print(f"{'Admins':<{max_key_length}}: {self.admi}")


def config_load(config_path):
    """
    Загружает конфигурацию из файла TOML.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
    
    try:
        with open(config_path, "r") as f:
            config_data = toml.load(f)
        return Config(config_data)
    except Exception as e:
        raise RuntimeError(f"Error loading configuration from '{config_path}': {e}") from e