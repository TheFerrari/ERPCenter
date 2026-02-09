.PHONY: up down logs migrate upgrade downgrade test

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose run --rm backend alembic -c /app/alembic.ini revision --autogenerate -m "auto"

upgrade:
	docker compose run --rm backend alembic -c /app/alembic.ini upgrade head

downgrade:
	docker compose run --rm backend alembic -c /app/alembic.ini downgrade -1

test:
	docker compose run --rm backend pytest
