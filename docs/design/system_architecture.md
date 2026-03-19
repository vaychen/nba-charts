# System architecture

## Intent

- keep local sample-data POCs fast to build
- add a stable backend shape that can grow into a Postgres-backed analytics service
- let one API layer support Dash, future custom frontends, and BI tools

## Current and target shape

```mermaid
flowchart LR
    subgraph Sources
        sample[Sample files\nJSON and CSV]
        nba[Live NBA APIs]
        future[Future external APIs]
    end

    subgraph Ingestion
        etl[ETL jobs\nsync_reference + future ingestors]
    end

    subgraph Storage
        postgres[(Postgres\nraw, staging, marts)]
    end

    subgraph Backend
        services[Python service layer]
        api[FastAPI]
    end

    subgraph Clients
        dash[Dash + Plotly]
        echarts[ECharts app]
        d3[D3 app]
        bi[Power BI / Tableau]
    end

    sample --> services
    sample --> api
    nba --> etl
    future --> etl
    etl --> postgres
    postgres --> services
    services --> api
    api --> dash
    api --> echarts
    api --> d3
    api --> bi
```

## Runtime request flow

```mermaid
sequenceDiagram
    actor User
    participant Client as Dash or future client
    participant API as FastAPI
    participant Service as Service layer
    participant Store as Sample file or Postgres

    User->>Client: Choose filters and season
    Client->>API: Request report data
    API->>Service: Validate inputs and build query scope
    Service->>Store: Load curated dataset
    Store-->>Service: Rows and aggregates
    Service-->>API: Response payload
    API-->>Client: JSON
```

## What is true today

- the `fg3m` report and Kobe shot POC are sample-data backed
- reference-data sync commands already target PostgreSQL for players and teams
- the shot-chart endpoints still call live NBA APIs directly

## Target operating model

- ETL jobs ingest from external APIs into Postgres
- FastAPI reads curated tables or views instead of hitting external APIs on demand
- UI clients stay thin and focus on interaction, not data shaping
- sample files remain useful for tests, demos, and offline prototyping

## Why this matters before adding more APIs

- API rate limits and response changes are easier to absorb in ETL than in request-time code
- snapshots make historical analytics reproducible
- one database model is easier to join and index than many raw files or live API responses
- the same backend can feed Dash now and ECharts, D3, or BI later
