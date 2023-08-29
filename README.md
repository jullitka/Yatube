# Yatube
Проект социальной сети Yatube.

Позволяет регестрироваться на сайте и делать публикации с фото. Публикации можно размещать в тематических группах.

Также можно просматривать и комментировать публикации других пользователей и подписываться на понравившихся авторов.


## Стек технологий
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

## Запуск проекта:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/jullitka/hw05_final.git

cd hw05_final
```
Cоздать и активировать виртуальное окружение:

```
python -m venv env

source venv/Scripts/activate

python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Перейти в необходимую директорию и выполнить миграции:
```
cd yatube

python manage.py migrate
```
Запустить проект:
```
python manage.py runserver
```
