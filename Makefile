setup:
	pip install -r requirements.txt

serve:
	FLASK_APP=main.py FLASK_ENV=development flask run
