# Hub share for EDA

How one teammate uploads the workspace EDA and the others restore
it. SKILL.md has the gate; this file has the procedure.

Hub `Project.put` only accepts an `EstimatorReport` or
`CrossValidationReport`. The EDA files ride on `EDACarrier`
(`templates/eda_carrier.py`). Confirm every `skore` symbol via
`python-api` this turn.

Reserved key: **`eda`**. Never an experiment stem. Never `put` a
model under it.

## When this applies

Only when `skore mode:` is **hub**. Local / mlflow: no Hub lookup,
no wait-for-teammate; G-EDA stays **run / skip**.

Copy `templates/eda_carrier.py` to `src/<pkg>/eda_carrier.py` if
that file is missing **before** `put` or `get`. Import it before
`get` so unpickle resolves `EDACarrier`. Producer and consumers
must share the same package name (same repo).

Sharing is **not** inside `data/eda.py`. Copy
`templates/share_eda.py` to `scratch/eda/share.py`, substitute,
set `MODE`, run. That file is the only scratch script allowed to
`evaluate` / `put`, and only for key `eda`.

## Decision flow (hub mode, every G-EDA)

Do this **before** placing `data/eda.py` or asking run / skip.

```
1. Copy eda_carrier.py into src/<pkg>/ if missing.
2. MODE=lookup on Hub (summarize → row with key == "eda").
3. Key present?
     yes, local data/eda.md missing or JOURNAL Status is waiting
          → MODE=fetch, write data/eda.py + eda.md + eda_*.html,
            JOURNAL Status: done (fetched). STOP (EDA done).
     yes, local files already present
          → STOP (EDA done). Do not re-fetch unless the user
            asked to refresh.
     no, local data/eda.py + eda.md + HTML already present
          → MODE=put (share what is already on disk), then STOP.
     no, local files missing
          → AskUserQuestion (see below). Do NOT skip. Do NOT
            draft the baseline.
```

### Ask when Hub has no `eda` yet

Tell the user there is **no existing EDA on Hub**. Ask:

> No EDA under key `eda` on Hub. Run it now, or wait for a
> teammate who is already computing it?

Options:

- **run** — compute locally, then `MODE=put`. Needs the agent
  feature (`ipython`). Decline install → stay blocked (do not
  pretend EDA is skipped so modelling can start).
- **wait** — a teammate is already running EDA and has not
  `put` yet. JOURNAL `Status: waiting`. **STOP.** Do not draft
  `01_baseline`. Do not run EDA. Do not treat this as skip.

Free-text "go fast" / "quick baseline" does **not** resolve this
ask.

### Resume after waiting

Next user turn (or when they say the teammate uploaded / they
want to run it themselves): **lookup Hub again first**.

- Key present → fetch, JOURNAL `done (fetched)`, continue
  bootstrap.
- Key still missing → ask again: keep **waiting**, or **run**
  it yourself now.

Do not busy-loop `sleep` + lookup in one turn. Wait means the
modelling work stops until Hub has the report or the user
chooses **run**.

## Put (after a local run)

Only after `data/eda.py`, `data/eda.md`, and at least one
`data/eda_<table>.html` exist.

1. `MODE=put`: read those files into `EDACarrier`.
2. `X`, `y` = the **same target-bearing table** EDA used (full
   table, not a sample). Hub's data view should match EDA.
3. Fit the carrier; build a report that holds that **full**
   table (prefer `evaluate(..., splitter="prefit")` after fit —
   confirm via `python-api`). Do not use a random 80/20 split
   just because that is the evaluate default.
4. `project.put("eda", report)`.
5. JOURNAL: `Status: done`, Hub URL if `put` printed one.

If `put` fails, local EDA still counts as **done**; warn. Do not
block a solo run on Hub errors.

Re-running EDA overwrites local files and `put`s again under the
same key (Hub keeps history; the key points at the new report).

## Fetch

1. Import `EDACarrier` first.
2. `MODE=fetch`: `get` by **id** from the lookup frame, not by
   key.
3. Read `eda_py`, `eda_md`, `html_by_table` off the fitted
   estimator (confirm the report attribute via `python-api`).
4. Write `data/eda.py`, `data/eda.md`, and each `eda_*.html`.
   Refuse HTML keys that are not `eda_*.html` filenames.
5. Do **not** execute `data/eda.py` after fetch.
6. JOURNAL: `Status: done (fetched)`, Hub URL / id.

Fetch does not need `ipython`.

## JOURNAL lines (hub)

```
- **Status:** done | done (fetched) | waiting | skipped - <YYYY-MM-DD>
- **Summary:** ...
- **Report:** [data/eda.md](../data/eda.md)
- **Hub:** <URL or `skore:report:…` id | n/a>
```

`skipped` is **local / mlflow only**. Hub mode uses **run** or
**wait**, not skip.

## Failure modes

| Symptom | Cause | What to do |
|---|---|---|
| `KeyError` on `project.get("eda")` | `get` is by id | lookup frame → `id` → `get(id)` |
| Unpickle `AttributeError` / `ModuleNotFoundError` | `eda_carrier.py` missing or different `<pkg>` | copy the template; same package name as producer |
| Lookup finds no `eda` after teammate "finished" | they have not `put`, or different Hub project / workspace | re-check workspace + project name; keep waiting or run |
| Proceeded to `01_baseline` while Status is `waiting` | treated wait as skip | STOP, delete that draft if it was created this turn, resume G-EDA |
| `put` under `01_*` "as the EDA" | wrong key | `eda` only |
