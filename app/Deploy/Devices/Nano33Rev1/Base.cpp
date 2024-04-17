#include <Wire.h>
#include "model.hpp"
#include <ArduinoBLE.h>
{% for item in includes %}
    {{item}} 
{% endfor %}

{% for item in before_setup %}
    {{item}} 
{% endfor %}

{% if "BLE_DEPLOY" in additionalSettings %}
    BLEService predictionService("{{additionalSettings["BLE_DEPLOY"]["serviceUUID"]}}");
    BLEIntCharacteristic predictionCharacteristic("{{additionalSettings["BLE_DEPLOY"]["characteristicUUID"]}}", BLERead | BLENotify);
{% endif %}

extern TwoWire Wire1;

void setup()
{

    Serial.begin(9600);
    delay(500);
    Serial.println("StartUp!!!");

    {% for item in setup %}
        {{item}}
    {% endfor %}

    {% if "BLE_DEPLOY" in additionalSettings %}
        if (!BLE.begin())
    {
        Serial.println("Starting BLE failed!");
        while (1);
    }
        BLE.setLocalName("OpenEarable");

        BLE.setAdvertisedService(predictionService);
        predictionService.addCharacteristic(predictionCharacteristic);
        BLE.addService(predictionService);
        // Start advertising
        BLE.advertise();
    {% endif %}

    // Other setup code if needed
}

void loop()
{
    {% if "BLE_DEPLOY" in additionalSettings %}
    BLE.poll();
    {% endif %}
    static auto lastChecked = millis();
    static auto lastPredict = millis();

    if (millis() - lastChecked >= ({{sampling_rate}}))
    {

        {% for item in before_obtain_values %}
            {{ item }}
        {% endfor %}

        {% for item in obtain_values %}
            {{ item }}
        {% endfor %}
        add_datapoint({{add_datapoint_vars}});
        lastChecked = millis();
    }

    if (millis() - lastPredict >= (1000 / {{classification_frequency}}))
    {
        int res = predict();
        Serial.print(millis());
        Serial.print(" <==> ");
        Serial.print("Prediction: ");
        Serial.println(res);

        {% if "BLE_DEPLOY" in additionalSettings %}
        predictionCharacteristic.writeValue(res);
        {% endif %}
        lastPredict = millis();
    }
}
