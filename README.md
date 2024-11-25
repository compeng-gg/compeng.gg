# CompEng.gg

A site for learning coding.

## Frontend

Setting up

```
cd frontend
npm i
```

Running

```
cd frontend
npm run dev
```

## Backend

Setting up

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python manage.py migrate
daphne compeng_gg.asgi:application
```

Running

```
cd backend
source venv/bin/activate
daphne compeng_gg.asgi:application
```

Run Unit Tests

```
cd backend
pytest
```
