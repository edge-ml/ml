#ifndef EDGEMLPIPELINE_HPP
#define EDGEMLPIPELINE_HPP

#ifdef __EMSCRIPTEN__
#include <emscripten/bind.h>
#endif

#include <vector>
#include <string>
{% for include in includes %}
    {{ include }}
{% endfor %}

#define Matrix vector<vector<float>>



{% for global in globals %}
    {{ global }}
{% endfor %}

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


{% for step in steps %}
    {{step}}
{% endfor %}

int predict() {
    {% for step in predictSteps %}
        {{step}}
    {% endfor %}
}

#ifdef __EMSCRIPTEN__
EMSCRIPTEN_BINDINGS(my_module) {
    emscripten::function("predict", &predict);
    emscripten::function("add_datapoint", &add_datapoint);
    emscripten::function("class_to_label", &class_to_label);
}
#endif

#endif