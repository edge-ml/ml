#include "tensorflow/lite/micro/kernels/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"
#include "Arduino_BHY2.h"

#include "model_data.cc"

const tflite::Model* model;
tflite::MicroErrorReporter* error_reporter;
tflite::AllOpsResolver* resolver;
tflite::MicroInterpreter* interpreter;

{% for item in before_setup %}
{{ item }}
{% endfor %}

void setup() {
  Serial.begin(115200);
  BHY2.begin();

  static tflite::MicroErrorReporter micro_error_reporter;
  error_reporter = &micro_error_reporter;

  model = tflite::GetModel(converted_model_tflite);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    error_reporter->Report(
        "Model provided is schema version %d not equal "
        "to supported version %d.",
        model->version(), TFLITE_SCHEMA_VERSION);
    return;
  }

  static tflite::AllOpsResolver resolver;

  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, tensor_arena_size, error_reporter);
  interpreter = &static_interpreter;

  {% for item in setup %}
  {{ item }}
  {% endfor %}
}

void loop() {
  static auto lastCheck= millis();
  static auto lastPredict = millis();
  BHY2.update();

  if (millis() - lastCheck >= (1000 / {{sampling_rate}})) {
    {% for item in obtain_values %}
    {{ item }}
    {% endfor %}
    add_datapoint({{add_datapoint_vars}});
    lastCheck = millis();
  }
  if (millis() - lastPredict >= 1000) {
    // Inference
    lastPredict = millis();
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
      error_reporter->Report("Invoke failed.");
    }

    float result = interpreter->output(0)->data.f[0];
    Serial.println(result);
  }
}