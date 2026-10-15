Models pickled by scikit-learn 1.0.2 (numpy 1.21.6), the version older edge-ml
models were trained with, plus their predictions as reference. Used by
tests/test_legacy_sklearn.py. Regenerate with:

    docker run --rm -v $PWD:/out -w /out python:3.9-slim sh -c \
      "pip install scikit-learn==1.0.2 numpy==1.21.6 && python make_legacy.py /out"
