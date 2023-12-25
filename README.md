# Yatube
### О проекте:
Социальная сеть для публикации блогов. Предусмотрена возможность объединения пользователей в сообщества.
Настроена регистрация и сессионная авторизация

### Запуск проекта:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/avpech/hw05_final.git
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Script/activate
```
Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Перейти в каталог yatube:
```
cd yatube
```
Выполнить миграции:
```
python manage.py migrate
```
Запустить проект:
```
python manage.py runserver
```
##### Об авторе
Артур Печенюк
- :white_check_mark: [avpech](https://github.com/avpech)
