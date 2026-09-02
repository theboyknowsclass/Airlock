# Airlock — Architecture

Every package a build depends on is resolved against a canonical store,
scanned by a horizontally-scaled worker pool behind RabbitMQ, and — with one
deliberate exception — always signed off by a human before it's trusted. A
second, independent loop keeps released packages under ongoing watch after
they ship. Full detail in `spec.md`; schema in `data-model.md`.

## Fig. 1 — The Request Pipeline

```mermaid
flowchart TD
    BS["Build System<br/>CI/CD · API key"]
    DEV["Developer<br/>manual upload · OIDC"]
    API["API — FastAPI<br/>auth · parse lock file · enqueue"]
    PG[("PostgreSQL<br/>packages · requests · applications<br/>license policy · audit log")]
    MQ[["RabbitMQ<br/>durable queue, dedup by (eco, name, version)"]]
    WK["Workers — Python<br/>horizontally scaled"]

    subgraph SCAN["Scan Pipeline"]
        INT["Integrity verification"]
        VULN["Vulnerability scan — OSV · NVD · GHSA"]
        MAL["Malware / behavior scan"]
        LIC["License check — SPDX AND/OR"]
    end

    RUI["Review UI<br/>React / TypeScript"]
    APR{{"Approver<br/>OIDC · approver role"}}
    NEXUS[("Nexus Repository<br/>npm · PyPI · NuGet hosted repos")]

    BS -->|"POST /requests"| API
    DEV -->|"POST /requests/manual"| API
    API -.->|"poll GET /requests/{id}"| BS
    API -->|"check canonical store"| PG
    PG -.->|"resolved: approved / rejected"| API
    PG -->|"enqueue — package unknown"| MQ
    MQ --> WK
    WK -->|"run checks"| SCAN
    SCAN -->|"write findings + severity → pending_review"| PG
    PG -->|"pending_review queue"| RUI
    RUI <-->|"review"| APR
    APR ==>|"approve / reject — audited, always human"| PG
    PG ==>|"on approval only — push package"| NEXUS

    classDef actor stroke-dasharray: 5 5;
    classDef gate fill:#f2e3ce,stroke:#b5701c,stroke-width:2px;
    classDef auto fill:#dceeec,stroke:#1c7c74;
    class BS,DEV,APR actor
    class APR gate
    class MQ,WK,SCAN,INT,VULN,MAL,LIC auto
```

A clean scan never auto-approves — the one exception is a `banned` license,
which auto-rejects before reaching a human at all. Everything else, however
low-risk, waits for the Approver. Rejection is permanent for that exact
(package, version); the only way back in is a new version.

## Fig. 2 — The Watch List

*Independent of Fig. 1 — runs on its own schedule.*

```mermaid
flowchart LR
    REL(["on release<br/>(Fig. 1)"]) --> PG
    PG[("PostgreSQL<br/>released, watched packages")]
    SCHED["Scheduler<br/>polls hourly"]
    FEEDS["Vulnerability Feeds<br/>OSV · NVD · GitHub Advisories"]
    NOTIFY["Notification Layer<br/>in-app · email · Slack/Teams"]
    TEAM{{"Owning Team<br/>per Application"}}

    SCHED -->|"poll"| FEEDS
    FEEDS -.->|"diff vs. watched packages → VulnerabilityAlert"| PG
    PG -->|"always notifies"| NOTIFY
    NOTIFY --> TEAM

    classDef actor stroke-dasharray: 5 5;
    classDef auto fill:#dceeec,stroke:#1c7c74;
    class FEEDS,TEAM actor
    class SCHED auto
```

A hit never auto-revokes — that stays a manual action, same as everywhere
else an Approver makes the call. Retiring an `ApplicationVersion` removes
its `watch_list_entries` unless the package is still shared with another
active version.
