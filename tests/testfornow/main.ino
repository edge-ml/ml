#include "model.hpp"
#include "Arduino_BHY2.h"


  SensorXYZ accelerometer(SENSOR_ID_ACC);


void setup() {

  Serial.begin(115200);
  BHY2.begin();
    
    accelerometer.begin(40);
    
}

void loop() {
  static auto lastCheck= millis();
  static auto lastPredict = millis();
  BHY2.update();

  // Check sensor values every second  
  if (millis() - lastCheck >= (1000 / 1.0)) {
    
        short acc_x = accelerometer.x();
    
        short acc_y = accelerometer.y();
    
        short acc_z = accelerometer.z();
    
    add_datapoint(acc_x,acc_y,acc_z);
    lastCheck = millis();
  }
  if (millis() - lastPredict >= 1000) {
    lastPredict = millis();
    Serial.println(predict());
  }
}