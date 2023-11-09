#include <vector>
#include <string>
{% for include in includes %}
    {{ include }}
{% endfor %}

#define Matrix vector<vector<float>>



{% for global in globals %}
    {{ global }}
{% endfor %}

{% for step in steps %}
    {{step}}
{% endfor %}

int predict() {
    {% for step in predictSteps %}
        {{step}}
    {% endfor %}
}