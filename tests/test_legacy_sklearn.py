"""Models pickled by older scikit-learn versions (1.0.x) must still load,
predict exactly as before, and export to C.

Before sklearn_compat these failed with "node array from the pickle has an
incompatible dtype", which made every older Decision Tree / Random Forest model
undownloadable (HTTP 500)."""
import json
import os
import pickle
import sys
import unittest
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import test_torch_executorch  # noqa: E402,F401  (configures the environment before app imports)

from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402
from sklearn.tree._tree import Tree  # noqa: E402

from app.ml.Pipelines.Categories.Classifier import decision_tree, random_forest, sklearn_compat  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "legacy_sklearn")


def fixture(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


REF = json.loads(fixture("reference.json"))
X = np.array(REF["X_test"])


class TestLegacyPickles(unittest.TestCase):

    def test_fixtures_really_are_legacy(self):
        self.assertEqual(REF["sklearn"], "1.0.2")
        with self.assertRaisesRegex(ValueError, "incompatible dtype"):
            pickle.loads(fixture("dt.pkl"))

    def test_predictions_match_the_original_version(self):
        for name in ["dt", "rf"]:
            with self.subTest(model=name):
                model = sklearn_compat.loads(fixture(f"{name}.pkl"))
                np.testing.assert_array_equal(model.predict(X), REF[name]["predict"])
                np.testing.assert_allclose(model.predict_proba(X), REF[name]["proba"], atol=1e-12)

    def test_trees_are_plain_sklearn_trees(self):
        rf = sklearn_compat.loads(fixture("rf.pkl"))
        self.assertTrue(all(type(e.tree_) is Tree for e in rf.estimators_))
        # so the model can be pickled again without referencing sklearn_compat
        again = pickle.loads(pickle.dumps(rf))
        np.testing.assert_array_equal(again.predict(X), REF["rf"]["predict"])

    def test_current_pickles_load_unchanged(self):
        rng = np.random.default_rng(1)
        Xc, yc = rng.normal(size=(200, 4)), rng.integers(0, 3, 200)
        for model in [DecisionTreeClassifier(random_state=0).fit(Xc, yc),
                      RandomForestClassifier(n_estimators=5, random_state=0).fit(Xc, yc)]:
            with self.subTest(model=type(model).__name__):
                loaded = sklearn_compat.loads(pickle.dumps(model))
                np.testing.assert_array_equal(loaded.predict_proba(Xc), model.predict_proba(Xc))


class TestRestoreAndExport(unittest.TestCase):
    """The path a model download takes: restore the option from storage, then
    export it to C."""

    def _restore(self, module, cls, data):
        original = module.StorageProvider
        module.StorageProvider = SimpleNamespace(load=lambda data_id: data)
        try:
            option = cls(cls.get_parameters())
            option.restore(SimpleNamespace(
                state={"data_id": "legacy"}, parameters=cls.get_parameters(), input_shape=[9], output_shape=[1]
            ))
        finally:
            module.StorageProvider = original
        return option

    def test_legacy_decision_tree_restores_and_exports_c(self):
        option = self._restore(decision_tree, decision_tree.DecisionTree, fixture("dt.pkl"))
        np.testing.assert_array_equal(option.clf.predict(X), REF["dt"]["predict"])
        step = option.exportC(None)
        # the C template returns classes[leaf].argmax() for each leaf
        leaves = option.clf.apply(X)
        np.testing.assert_array_equal(
            [step.variables["classes"][leaf].argmax() for leaf in leaves], REF["dt"]["predict"]
        )

    def test_legacy_random_forest_restores(self):
        option = self._restore(random_forest, random_forest.RandomForest, fixture("rf.pkl"))
        np.testing.assert_array_equal(option.clf.predict(X), REF["rf"]["predict"])


if __name__ == "__main__":
    unittest.main()
