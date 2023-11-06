#include <RocksettaTensorFlowLite.h>

#include "model.h"
#include "normalizer.h"

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

SensorXYZ accelerometer(SENSOR_ID_ACC); // needs to be read from jinjaVars

constexpr int window_size = 5; // needs to be read from jinjaVars
constexpr int sensor_stream_count = 3; // needs to be read from jinjaVars
constexpr int num_classes = 2; // needs to be read from jinjaVars

float data_window[window_size * sensor_stream_count] = {0};
int data_count = 0;

constexpr int kTensorArenaSize = 1500; // if the program doesn't run try a higher value, it can be later optimized
uint8_t tensor_arena[kTensorArenaSize];
}  // namespace


void addDataPoint(float *data) {
  if (data_count < window_size) {
    for (int i = 0; i < sensor_stream_count; i++) {
      data_window[data_count * sensor_stream_count + i] = data[i]; 
    }
    data_count++;
  } else {
    // Slide the window
    for (int i = 0; i < window_size; i++) {
      for (int j = 0; j < sensor_stream_count; j++) {
        data_window[i * sensor_stream_count + j] = (i != window_size - 1) ? data_window[(i+1) * sensor_stream_count + j] : data[j];
      }
    }
  }
}

int getMostLikelyClass() {
  int prediction = -1;
  float probability = 0.f;
  for (int i = 0; i < num_classes; i++) {
    if (probability < output->data.f[i]) {
      prediction = i;
      probability = output->data.f[i];
    }
  }
  return prediction;
}

void printPrediction() {
  int prediction = getMostLikelyClass();
  switch (prediction) {
    case 0: Serial.println("Still"); break; // needs to be read from jinjaVars
    case 1: Serial.println("Moving"); break; // needs to be read from jinjaVars
    case default: Serial.println("")
  }
}

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

  static tflite::MicroMutableOpResolver<3> resolver;

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

  if (millis() - lastCheck >= (1000 / 1.0)) {

      float data[] = {accelerometer.x(), accelerometer.y(), accelerometer.z()}; // needs to be read from jinjaVars
      
      normalize(data);
      addDataPoint(data);

      Serial.println("Data window");
      for (int i = 0; i < window_size * sensor_stream_count; i++) {
        input->data.f[i] = data_window[i];
        Serial.print(data_window[i]);
        Serial.print(" ");
      }
      Serial.println("");
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

    prediction = interpreter->output(0)->data.f[0];
    char strBuf[100];
    sprintf(strBuf, "x = %f %f, y = %f %f, z = %f %f, prediction = %f %f", x, norm_x, y, norm_y, z, norm_z, interpreter->output(0)->data.f[0], interpreter->output(0)->data.f[1]);
    Serial.println(strBuf);
  }
}