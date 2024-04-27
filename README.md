# Параметры конфига

**bot_token** - Токен из @BotFather

**admins_channel** - id частного канала можно получить из @getmyid_bot 

**channel_id** -  id канала в который будут публиковаться посты

**footer_text** - Текст внутри футера, если не нужен то `footer_text=off`

**footer_link** - Ссылка внутри на которую будет вести текст, если не нужна `footer_link = off`

**Блок \[BD]** - настройки для подключения к БД

**host** - ip адрес БД, 127.0.0.1, если локально

**database** - Имя базы данных

**user и password** - Имя пользователя и пароль от которого идет подключение

# Настройка БД

Выполнить поочередно скрипты из файла `Create.sql`, сначала создать БД, переключится на неё и создать таблицу.

# Функции панели администратора

**/start** - Отображение команд и добавление клавиатуры

**/stat** - Запрос к боту и получение сообщение "Бот работает" если всё в порядке

**/all_news** - Запрос к БД и получение всех записей в таблице

**/restart** - Перезапуск бота, путем закрытия текущего экземпляра main и запуска нового

# Запуск бота

```sh
pip install -r requirements.txt
```

Затем

```sh
python main.py
```

# Настройка службы

Поменять значение `WorkingDirectory` в файле `suggest_news_bot.service`

Переместить файл службы в папку `/etc/systemd/system/`

Запустить службу и добавить в автозапуск

```sh
systemctl start suggest_news_bot.service
```
```sh
systemctl enable suggest_news_bot.service
```

Проверить статус

```sh
systemctl status suggest_news_bot.service
```

Либо, для просмотра логов службы команда 

```sh
journalctl -e -u suggest_news_bot.service
```
