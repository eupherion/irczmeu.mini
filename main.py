#!/usr/bin/env python3
import sys
import os
from core import Bot

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "./botsconf/config.toml"
    bot = Bot(config_file)
    bot.run()
