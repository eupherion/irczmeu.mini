import os
import glob
import importlib

# Получаем список всех .py файлов в mods
modules = [os.path.basename(f)[:-3] for f in glob.glob(
    os.path.join(os.path.dirname(__file__), "*.py")
    ) if not f.endswith("__init__.py")]

# Импортируем их
for module_name in modules:
    importlib.import_module('.' + module_name, package='mods')