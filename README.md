# Airlock

A package approval gateway that scans and gates every dependency — direct
and transitive — a build pulls in, to stop supply-chain attacks like the
Shai-Hulud npm worm from entering the org unreviewed.

- **Design docs**: [`docs/spec.md`](docs/spec.md) (full behavior spec),
  [`docs/data-model.md`](docs/data-model.md) (Postgres schema),
  [`docs/architecture.md`](docs/architecture.md) (diagrams),
  [`docs/constitution.md`](docs/constitution.md) (project standards).
- **This directory**: a **walking skeleton** — the thinnest real slice
  through the architecture, proving the queue-backed, restart-safe worker
  design (constitution Principle VIII) actually holds before building out
  the full system.

## What's implemented (and what isn't)

Implemented: `POST /requests` and `GET /requests/{id}` for the npm
ecosystem only, backed by RabbitMQ + a horizontally-scalable Python worker
pool running **integrity verification only**, writing results to
PostgreSQL, with a stub `POST /packages/{id}/decision` standing in for the
Review UI + Approver flow.

Deliberately **not** implemented yet (see `docs/spec.md` for the full
design): vulnerability/malware/license scanning, real OIDC/RBAC (build
systems use a plain API key; the decision endpoint takes any caller — every
stub is marked `TODO`/`STUB` in code), Nexus publishing, `Application` /
`ApplicationVersion` / watch list, real lock-file parsing (requests take a
pre-parsed `{name, version, integrity}` list rather than an actual
`package-lock.json`), and the React frontend.

## Run it

```sh
make up      # builds and starts postgres, rabbitmq, migrate, api, worker
make seed    # seeds a dev build-system API key: "dev-local-key"
```

API is at `http://localhost:8000` (`/healthz`), RabbitMQ management UI at
`http://localhost:15672` (airlock/airlock).

```sh
curl -X POST http://localhost:8000/requests \
  -H "Authorization: Bearer dev-local-key" -H "Content-Type: application/json" \
  -d '{"ecosystem":"npm","packages":[{"name":"is-number","version":"7.0.0"}]}'
# -> {"id": "...", "status": "pending", "packages": [...]}

curl http://localhost:8000/requests/<id>
# poll until status is no longer "pending"
```

Once a package reaches `pending_review` (check via the `GET /requests/{id}`
response, or query Postgres directly), stand in for the Approver:

```sh
curl -X POST http://localhost:8000/packages/<package_id>/decision \
  -H "X-Dev-User: alice" -H "Content-Type: application/json" \
  -d '{"decision":"approve"}'
```

## Prove the scaling / restart-safety claims

```sh
make scale-workers   # docker compose up -d --scale worker=3
docker compose kill worker   # kill mid-scan — RabbitMQ redelivers, nothing is lost
docker compose up -d worker
```

## Tests

BDD scenarios (Gherkin via `pytest-bdd`) exercise exactly these claims
end-to-end against the running `docker compose` stack — including actually
killing and restarting a worker mid-scan and asserting the job still
completes, not just that the happy path works:

```sh
make up && make seed
make test    # services/api/tests/features/package_request.feature
```

## Repo layout

```
services/api/        FastAPI app — auth, request/poll endpoints, enqueues scan jobs
services/worker/      RabbitMQ consumer — runs the scan pipeline, writes findings
migrations/           Alembic, plain SQL (no ORM shared with either service)
docker-compose.yml    postgres, rabbitmq, migrate, api, worker
```

`services/api` and `services/worker` share **no in-process code** on
purpose (constitution Principle VIII) — each owns its own DB access. That's
what makes it possible to later drop in a Go worker on the same queue and
benchmark it against the Python one without touching the API.
