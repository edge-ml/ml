#ifndef EDGEMLPIPELINE_HPP
#define EDGEMLPIPELINE_HPP

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
#endif