#include "model.hpp"
#include "Arduino_BHY2.h"

{% for item in before_setup %}
  {{ item }}
{% endfor %}

void setup() {

  Serial.begin(115200);
  BHY2.begin();
    {% for item in setup %}
    {{ item }}
    {% endfor %}
}

void loop() {
  static auto lastCheck= millis();
  static auto lastPredict = millis();
  BHY2.update();

  // Check sensor values every second  
  if (millis() - lastCheck >= (1000 / {{sampling_rate}})) {
    {% for item in obtain_values %}
        {{ item }}
    {% endfor %}
    add_datapoint({{add_datapoint_vars}});
    lastCheck = millis();
  }
  if (millis() - lastPredict >= 1000) {
    lastPredict = millis();
    Serial.println(predict());
  }
}