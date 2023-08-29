# hw05_final

### Запуск проекта:

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
