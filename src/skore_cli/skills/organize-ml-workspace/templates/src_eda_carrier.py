"""Sklearn estimator that carries EDA files through a skore report.

Hub ``Project.put`` only accepts an ``EstimatorReport`` /
``CrossValidationReport``. This estimator stores the workspace EDA
files as constructor parameters so they survive clone, joblib, and
``project.get`` on a teammate's machine.

Import this module **before** ``project.get`` so unpickle can resolve
the class. Teammates must use the same package name as the producer.
"""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin


class EDACarrier(BaseEstimator, RegressorMixin):
    """No-op regressor whose parameters are the EDA artifacts.

    Parameters
    ----------
    eda_py : str, default=""
        Full text of ``data/eda.py``.
    eda_md : str, default=""
        Full text of ``data/eda.md``.
    html_by_table : dict of str to str or None, default=None
        Mapping of filename (e.g. ``eda_train.html``) to HTML. ``None``
        means no HTML files. Do not put path separators in the keys.

    Attributes
    ----------
    n_features_in_ : int
        Number of features seen during ``fit``. Set so
        ``check_is_fitted`` / skore ``splitter="prefit"`` treat this
        estimator as fitted. ``clone`` still returns an unfitted copy.
    """

    def __init__(self, eda_py="", eda_md="", html_by_table=None):
        self.eda_py = eda_py
        self.eda_md = eda_md
        self.html_by_table = html_by_table

    def fit(self, X, y=None):
        """Fit: record feature count. File payloads stay on the parameters.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Feature table used for the Hub data view.
        y : array-like of shape (n_samples,), default=None
            Target for the Hub data view.

        Returns
        -------
        self : object
            Fitted estimator.
        """
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X):
        """Return zeros, one per row of ``X``.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Feature table.

        Returns
        -------
        ndarray of shape (n_samples,)
            Zeros. The predictions are unused; the files live on the
            estimator parameters.
        """
        n_samples = X.shape[0]
        return np.zeros(n_samples, dtype=float)
