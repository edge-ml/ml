"""Load scikit-learn models that were pickled by older scikit-learn versions.

Models trained before the scikit-learn upgrade (1.0.x -> 1.7) cannot be
unpickled anymore:

- scikit-learn 1.3 added a ``missing_go_to_left`` field to the tree node array,
  and ``Tree.__setstate__`` rejects node arrays without it.
- scikit-learn 1.4 stores class *proportions* in classifier tree leaves where
  older versions stored class *counts*. Loaded as-is, old trees would return
  wrong probabilities, and a random forest (which averages its trees'
  probabilities) could even predict a different class.
- Estimator parameters added since then (e.g. ``monotonic_cst``) are missing.

``loads`` upgrades such pickles while loading them; pickles written by the
current version load unchanged.
"""

import io
import pickle

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.tree._tree import Tree

_NODE_DTYPE = None


def _node_dtype():
    """The node dtype the installed scikit-learn expects, taken from a real tree."""
    global _NODE_DTYPE
    if _NODE_DTYPE is None:
        from sklearn.tree import DecisionTreeClassifier

        tree = DecisionTreeClassifier().fit([[0.0], [1.0]], [0, 1]).tree_
        _NODE_DTYPE = tree.__getstate__()["nodes"].dtype
    return _NODE_DTYPE


def _upgrade_nodes(nodes):
    expected = _node_dtype()
    if nodes.dtype == expected:
        return nodes
    upgraded = np.zeros(nodes.shape, dtype=expected)
    for name in nodes.dtype.names:
        upgraded[name] = nodes[name]
    # missing_go_to_left stays 0: old trees never saw missing values
    return upgraded


def _normalize_values(values):
    """Class counts -> class proportions per node and output (no-op if already
    proportions)."""
    sums = values.sum(axis=2, keepdims=True)
    if np.allclose(sums[sums > 0], 1.0):
        return values
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(sums > 0, values / sums, values)


class _LegacyTree(Tree):
    """Stand-in for sklearn's Tree while unpickling; upgrades old state."""

    def __setstate__(self, state):
        state = dict(state)
        state["nodes"] = _upgrade_nodes(state["nodes"])
        if self.max_n_classes > 1:  # classification tree
            state["values"] = _normalize_values(state["values"])
        super().__setstate__(state)


class _CompatUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "sklearn.tree._tree" and name == "Tree":
            return _LegacyTree
        return super().find_class(module, name)


def _as_plain_tree(tree):
    """Rebuild a _LegacyTree as a regular Tree, so nothing of this module
    stays referenced (e.g. if the model is pickled again)."""
    cls, args, state = tree.__reduce__()
    plain = Tree(*args)
    plain.__setstate__(state)
    return plain


def _fill_missing_attributes(estimator):
    """Give attributes that did not exist when the model was saved (new
    parameters like ``monotonic_cst``, or ``estimator`` which replaced
    ``base_estimator``) the value a fresh estimator gets."""
    try:
        fresh = type(estimator)()
    except Exception:
        return
    for key, value in vars(fresh).items():
        if key not in estimator.__dict__:
            setattr(estimator, key, value)


def _fix_estimator(obj):
    if isinstance(obj, BaseEstimator):
        _fill_missing_attributes(obj)
        tree = getattr(obj, "tree_", None)
        if isinstance(tree, _LegacyTree):
            obj.tree_ = _as_plain_tree(tree)
        for sub in getattr(obj, "estimators_", None) or []:
            _fix_estimator(sub)
        for attr in ("estimator", "base_estimator"):
            sub = obj.__dict__.get(attr)
            if isinstance(sub, BaseEstimator):
                _fill_missing_attributes(sub)
    return obj


def loads(data: bytes):
    """pickle.loads for scikit-learn models, also for ones saved by older
    scikit-learn versions."""
    return _fix_estimator(_CompatUnpickler(io.BytesIO(data)).load())
