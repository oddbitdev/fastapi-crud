# fastapi-crud

Example planning api using the Fast Api framework ,Uvicorn server and Sqlite. Creates workers and shifts, checks that no two shifts can occur on the same day or consecutive shifts on the previous or next day.

Shift format is:

1: 0 to 8

2: 8 to 16

3: 16 to 24

## To run the application locally
1. Clone this Repo `git clone https://github.com/oddbitdev/fastapi-crud`
2. Cd into the Fast-Api folder `cd fastapi-crud`
3. Create a virtualenv `python3 -m virtualenv .venv`
4. Activate virtualenv `source .venv/bin/activate`
5. Install requirements `pip install -r requirements.txt`
6. Start the app using Uvicorn `uvicorn app.main:app --reload`
7. Api documentation generated on [docs](http://127.0.0.1:8000/docs)


Run tests with `pytest .`


## To run locally on Docker
1. Clone this Repo `git clone https://github.com/oddbitdev/fastapi-crud`
2. Cd into the Fast-Api folder `cd fastapi-crud`
3. Build `docker-compose up -d --build`
4. Api documentation generated on [docs](http://127.0.0.1:8002/docs)


Run tests with `docker-compose exec app pytest .`
