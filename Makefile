.PHONY: up down logs seed test scale-workers

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f api worker

# Seeds a dev build-system API key ("dev-local-key") used by the BDD tests
# and for manual curl'ing against the API.
seed:
	docker compose exec -T postgres psql -U airlock -d airlock -c \
		"INSERT INTO build_systems (name, api_key_hash) VALUES ('dev', '$$(python3 -c "import hashlib; print(hashlib.sha256(b'dev-local-key').hexdigest())")') ON CONFLICT (name) DO NOTHING;"

test:
	cd services/api && pip install -e '.[dev]' -q && \
		AIRLOCK_TEST_API_URL=http://localhost:8000 \
		AIRLOCK_TEST_DATABASE_URL=postgresql://airlock:airlock@localhost:5432/airlock \
		pytest -v

# Proves the "horizontally scaled workers" claim (constitution Principle
# VIII) rather than just asserting it.
scale-workers:
	docker compose up -d --scale worker=3
