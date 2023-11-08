constexpr int num_classes = {{labels|length}};

std::string classToLabel(int cls) {
    switch (cls) {
    {% for label in labels %}   case {{loop.index0}}: return "{{label}}";
    {% endfor -%}
    }
    return "";
}

int getMostLikelyClass(float* logits) {
  int prediction = -1;
  float probability = 0.f;
  for (int i = 0; i < num_classes; i++) {
    if (probability < logits[i]) {
      prediction = i;
      probability = logits[i];
    }
  }
  return prediction;
}