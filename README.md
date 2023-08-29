# Yatube
Проект социальной сети Yatube.

Позволяет регестрироваться на сайте и делать публикации с фото. Публикации можно размещать в тематических группах.

Также можно просматривать и комментировать публикации других пользователей и подписываться на понравившихся авторов.

#### Зарегистрированные пользователи могут:

- Создавать публикации
- Просматривать, редактировать и удалять свои публикации
- Создавать/удалять/редактировать собственные комментарии к любым публикациям
- Подписываться на других пользователей и просматривать свои подписки.
- Просматривать информацию о сообществах и публикации в них.

#### Анонимные пользователи могут:

- Просматривать публикации
- Просматривать информацию о сообществах и публикации в них
- Просматривать комментарии
  
## Стек технологий
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

## Запуск проекта:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/jullitka/Yatube.git
cd Yatube
```
Cоздать и активировать виртуальное окружение:

```
python -m venv env
```
Для Linux
    ```
    source venv/bin/activate
    ```
    
Для Windows
    ```
    source venv/Scripts/activate
    ```

Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Перейти в необходимую директорию и выполнить миграции:
```
cd yatube
python yatube/manage.py makemigrations
python manage.py migrate
```
Запустить проект:
```
python manage.py runserver
```
После запуска проект доступен в браузере по адресу  http://127.0.0.1:8000/
## Авторы
[Юлия Пашкова](https://github.com/Jullitka)
