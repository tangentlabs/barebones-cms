.PHONY: build_full remove_pyc update_virtualenv remove_db create_db quick_create_db test build_quick install

remove_pyc:
	-find . -type f -name "*.pyc" -delete

update_virtualenv:
	pip install -r requirements.txt

remove_db:
	python manage.py reset_db --router=default --noinput

create_db:
	python manage.py syncdb --noinput
	python manage.py migrate

quick_create_db:
	python manage.py migrate --fake

build_full: remove_pyc update_virtualenv remove_db create_db

build_quick: remove_pyc update_virtualenv remove_db quick_create_db

install: build_full

