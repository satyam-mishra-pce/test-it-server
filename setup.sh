python -m venv venv
source venv/bin/activate
pip install poetry
poetry install
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver
