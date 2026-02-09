.PHONY: up down logs migrate upgrade downgrade test seed

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic revision --autogenerate -m "auto"

upgrade:
	docker compose exec backend alembic upgrade head

downgrade:
	docker compose exec backend alembic downgrade -1

test:
	docker compose exec backend pytest -q

seed:
	docker compose exec backend python -m app.seed
