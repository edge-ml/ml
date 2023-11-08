#include <RocksettaTensorFlowLite.h>

#include "model_data.hpp"
#include "normalizer.hpp"
#include "windower.hpp"
#include "predictor.hpp"

#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"

#include "Arduino_BHY2.h"

// Globals, used for compatibility with Arduino-style sketches.
namespace {
tflite::ErrorReporter* error_reporter = nullptr;
const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;
{% for item in before_setup %}
{{ item }}
{% endfor %}
constexpr int kTensorArenaSize = 1500; // if the program doesn't run try a higher value, it can be later optimized
uint8_t tensor_arena[kTensorArenaSize];
}  // namespace

void setup() {
  Serial.begin(115200);
  BHY2.begin();
  static tflite::MicroErrorReporter micro_error_reporter;
  error_reporter = &micro_error_reporter;

  model = tflite::GetModel(g_model);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    TF_LITE_REPORT_ERROR(error_reporter,
                         "Model provided is schema version %d not equal "
                         "to supported version %d.",
                         model->version(), TFLITE_SCHEMA_VERSION);
    return;
  }

  static tflite::MicroMutableOpResolver<3> resolver; // needs to be read from jinjaVars

  resolver.AddFullyConnected(); // needs to be read from jinjaVars
  resolver.AddSoftmax(); // needs to be read from jinjaVars
  resolver.AddRelu(); // needs to be read from jinjaVars

  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
  interpreter = &static_interpreter;

  TfLiteStatus allocate_status = interpreter->AllocateTensors();
  if (allocate_status != kTfLiteOk) {
    TF_LITE_REPORT_ERROR(error_reporter, "AllocateTensors() failed");
    return;
  }

  input = interpreter->input(0);
  output = interpreter->output(0);

  accelerometer.begin(40); // needs to be read from jinjaVars
}

void loop() {
  static auto lastCheck = millis();
  static auto lastPredict = millis();
  BHY2.update();

  // Check sensor values every second 
  if (millis() - lastCheck >= (1000 / {{sampling_rate}})) {
      {% for item in obtain_values %}
      {{ item }}
      {% endfor %}
      float data[] = { {{add_datapoint_vars}} };

      normalize(data);
      addDataPoint(data);

      // Update the input tensor
      for (int i = 0; i < window_size * sensor_stream_count; i++) {
        input->data.f[i] = data_window[i];
      }
      lastCheck = millis();
  }
  if (millis() - lastPredict >= 1000) {
    // Inference
    lastPredict = millis();
    
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
      Serial.println("Invoke failed.");
      while(true) {
        // lock
      }
      
    }
    Serial.println(classToLabel(getMostLikelyClass(output->data.f)).c_str());
  }
}