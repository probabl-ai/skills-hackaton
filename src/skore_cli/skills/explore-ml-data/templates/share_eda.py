"""Lookup, fetch, or put workspace EDA on Skore Hub (key ``eda``).

Owned by ``explore-ml-data``. Copy to ``scratch/eda/share.py``,
substitute placeholders, set ``MODE``, run once. Confirm ``Project``,
``evaluate``, ``summarize``, and the fitted-estimator attribute via
``python-api`` this turn — do not copy signatures from memory.
"""

from __future__ import annotations

from pathlib import Path

from skore import Project, evaluate, login

from <pkg> import PROJECT_ROOT
from <pkg>.eda_carrier import EDACarrier
from <pkg>.hub import load_skore_credentials

EDA_KEY = "eda"
EDA_DIR = PROJECT_ROOT / "data"
MODE = "<MODE>"  # lookup | fetch | put

cfg = load_skore_credentials()
login(mode="hub")
project = Project(
    name="<project-name>",
    mode="hub",
    workspace=cfg["workspace"],
)


def _summary_frame(project):
    summary = project.summarize()
    frame = summary.frame() if hasattr(summary, "frame") else summary
    if hasattr(frame, "reset_index"):
        frame = frame.reset_index()
    return frame


def _eda_id(frame):
    rows = frame[frame["key"] == EDA_KEY]
    if len(rows) == 0:
        return None
    if "id" in rows.columns:
        return rows["id"].iloc[0]
    return rows.index[0]


def _fitted_estimator(report):
    for attr in ("estimator_", "estimator"):
        est = getattr(report, attr, None)
        if est is not None:
            return est
    raise AttributeError(
        "Could not find the fitted estimator on the report. "
        "Confirm the attribute via python-api."
    )


if MODE == "lookup":
    frame = _summary_frame(project)
    eda_id = _eda_id(frame)
    print({"eda_key_present": eda_id is not None, "id": eda_id})

elif MODE == "fetch":
    frame = _summary_frame(project)
    eda_id = _eda_id(frame)
    if eda_id is None:
        raise LookupError(f"No report under key={EDA_KEY!r} on Hub.")
    report = project.get(eda_id)
    est = _fitted_estimator(report)
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    (EDA_DIR / "eda.py").write_text(est.eda_py, encoding="utf-8")
    (EDA_DIR / "eda.md").write_text(est.eda_md, encoding="utf-8")
    html_by_table = est.html_by_table or {}
    written = ["eda.py", "eda.md"]
    for name, html in html_by_table.items():
        filename = Path(name).name
        if not filename.startswith("eda_") or not filename.endswith(".html"):
            raise ValueError(f"Refusing to write unexpected HTML name: {name!r}")
        (EDA_DIR / filename).write_text(html, encoding="utf-8")
        written.append(filename)
    print({"restored": written, "id": eda_id})

elif MODE == "put":
    eda_py = (EDA_DIR / "eda.py").read_text(encoding="utf-8")
    eda_md = (EDA_DIR / "eda.md").read_text(encoding="utf-8")
    html_by_table = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(EDA_DIR.glob("eda_*.html"))
    }
    X = <LOAD_X>
    y = <LOAD_Y>
    est = EDACarrier(eda_py=eda_py, eda_md=eda_md, html_by_table=html_by_table)
    est.fit(X, y)
    # Prefer a report that holds the *full* table (not an 80/20 split).
    # Confirm splitter="prefit" (or EstimatorReport kwargs) via python-api.
    report = evaluate(est, X, y, splitter="prefit")
    project.put(EDA_KEY, report)
    print({"put_key": EDA_KEY, "n_html": len(html_by_table)})

else:
    raise ValueError(f"MODE must be lookup, fetch, or put; got {MODE!r}")
