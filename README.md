# Energy Bills Automation

ETL pipeline that ingests Cosmote energy billing data from Vertica,
applies processing, and generates monthly billing reports.

## Setup (local / Workbench)

    uv sync                                # install deps from uv.lock
    cp dev.env.example ~/dev.env           # then fill in real credentials
    uv run jupyter lab                     # open Energy_Bills.ipynb

## Required environment

Create `~/dev.env` with:

    VERTICA_HOST=energy-up01
    VERTICA_PORT=5433
    VERTICA_USER=energy_user
    VERTICA_PASSWORD=<secret>
    VERTICA_DATABASE=ote_energydb

## Deployment to Posit Connect

    uv export --format requirements-txt --no-hashes --no-dev --no-emit-project --frozen > requirements.txt
    rsconnect deploy manifest manifest.json --name ote-connect

On Connect, credentials come from the **Vars** tab of the content item,
not from `dev.env`.

## Project layout

    Energy_Bills.ipynb        — main pipeline
    utils/                    — helpers (logger, profiler, data_process, …)
    data/                     — reference CSVs (tariffs, coordinates, …)
    pyproject.toml + uv.lock  — dependency manifest