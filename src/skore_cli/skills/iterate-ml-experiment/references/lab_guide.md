# Lab guide

Load this when `docs/GUIDED.md` exists in the project. The guide and
`docs/CONTEXT.md` are the brief. This file does not restate their
steps. Read both documents, then apply the rules below.

If `docs/GUIDED.md` is absent, ignore this file and keep the generic
experiment loop.

## Goal

Propose this sentence, and let the student amend it:

> minimize RMSE for the true OFF MDS-UPDRS motor score, on patients
> held out from training

Clinic ON/OFF scores are biased. The target column is the unbiased
score. The Kaggle holdout is by `patient_id`, not by visit.

## Shared EDA

The hub key `eda` is reserved for the exploratory files
(`data/eda.py`, `data/eda.md`, `data/eda_<table>.html`). Never `put`
a model report under `eda`.

Before `G-EDA` runs:

1. Look up the installed `skore` Project API with `python-api` and
   list keys in the team hub project (`load_skore_credentials()`,
   then `login(mode="hub")`). Do not invent a storage method.
2. Key `eda` already present → fetch those files into `data/` and
   do not compute a second EDA. Record JOURNAL status `done`.
3. A teammate is still computing it → ask the student to **wait**.
   Do not start a second run, and do not skip ahead to a model.
4. Key absent → one person may **run**. After the files exist, store
   them under `eda` with the API looked up above.

## What to propose next

Infer the unfinished section from artifacts. Suggest that section.
Do not block a student who names a later model; say which guide
section that request skips, then do what they asked.

| Evidence the section is still open | Suggest |
|---|---|
| No `data/eda.md` and no hub key `eda` | Shared EDA |
| EDA present, no hub report `01_dummy` | Dummy mean, RMSE, row holdout |
| `01_dummy` present, no `02_ridge` | Ridge on the same row holdout |
| `02_ridge` present, no `submission.csv` | The guide's Kaggle upload for that Ridge |
| A row-holdout Ridge report exists, and no grouped-CV report does | Patient-grouped CV |
| Those are done | The next section heading in `docs/GUIDED.md` |

Hub report keys come from the guide (`01_dummy`, `02_ridge`, …).
One new key per Kaggle file.

## Row holdout, then grouped CV

`01_dummy` and `02_ridge` call `skore.evaluate` with `splitter=0.2`
(a random visit holdout). Do not ask `G-CV-SPLITTER` for those two.
The leak (the same `patient_id` on both sides) is the point of that
holdout.

`G-CV-SPLITTER` opens on the guide's patient-grouped section, or
when the student asks for a grouped split earlier. The guide's
family is `GroupKFold` on `patient_id`. Record the student's answer
if they pick a different family.

## Kaggle file

`submission.csv` has header `Index,target`, one row per test visit.
The Kaggle submission description must contain the
`https://ibm.skore.probabl.ai/…` URL printed for that model's hub
report. A score without that URL does not count.
