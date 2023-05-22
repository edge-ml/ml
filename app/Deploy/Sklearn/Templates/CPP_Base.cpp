#include <vector>
#include <string>
{% for include in includes %}
    {{ include }}
{% endfor %}

#define Matrix vector<vector<float> >

float get_sampling_rate() {
    return {{samplingRate}};
}

string class_to_label(int cls) {
    {% for (k, label) in enumerate(labels) %}
        if (cls == {{k}}) {
            return "{{label}}";
        }
    {% endfor %}
    return "";
}

{% for global in globals %}
    {{ global }}
{% endfor %}

{{ classifier }}

{{ featureExtractor }}

{{ normalizer }}

{{ windower }}

int predict() {
    extract_features(raw_data, features);
    normalize(features);
    return predict(features);
}