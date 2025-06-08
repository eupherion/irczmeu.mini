#### Описание:
Простой IRC-бот на Python, в данном виде больше является шаблоном для расширения функционала.

#### Возможности:
- Подключение к IRC-серверу
- Обработка команд от пользователей
- Поддержка модулей команд

#### Установка:
```bash
git clone https://github.com/aeshmann/irc.bot.zmeu
cd irc.bot.zmeu
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> ⚙️ Настройки бота находятся в файле `./botconfigs/config.toml`.
#### Запуск:
```bash
main.py # по умолчанию использует конфиг ./botconfigs/config.toml
```
или 
```bash
main.py ./botconfigs/rizon.toml # аргументом указать путь к конфигу
```

