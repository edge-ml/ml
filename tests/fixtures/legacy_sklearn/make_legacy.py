"""Train trees with an old scikit-learn and save pickles + reference outputs."""
import json, pickle, sys
import numpy as np, sklearn
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

out = sys.argv[1]
rng = np.random.default_rng(0)
X = rng.normal(size=(400, 9)); y = (X[:, 0] + X[:, 3] > 0).astype(int) + (X[:, 5] > 1).astype(int)
Xt = rng.normal(size=(60, 9))
models = {
    "dt": DecisionTreeClassifier(max_depth=6, random_state=0).fit(X, y),
    "rf": RandomForestClassifier(n_estimators=12, max_depth=5, random_state=0).fit(X, y),
}
ref = {"sklearn": sklearn.__version__, "numpy": np.__version__, "X_test": Xt.tolist()}
for name, m in models.items():
    open(f"{out}/{name}.pkl", "wb").write(pickle.dumps(m))
    ref[name] = {"predict": m.predict(Xt).tolist(), "proba": m.predict_proba(Xt).tolist()}
json.dump(ref, open(f"{out}/reference.json", "w"))
print("made with sklearn", sklearn.__version__, "numpy", np.__version__)
