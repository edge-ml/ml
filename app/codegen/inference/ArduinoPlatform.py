from time import time
from app.codegen.inference.BasePlatform import BasePlatform
from app.codegen.inference.InferenceFormats import InferenceFormats


class ArduinoPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "cpp"

    def supported_formats(self):
        return [InferenceFormats.C_EMBEDDED, InferenceFormats.CPP]

    def codegen(self, window_size, timeseries, labels, format):
        temp = []
        temp.append(f'#include "___DOWNLOADED_MODEL_BASENAME___.hpp"')
        temp.append("")
        temp.append("String label;")
        temp.append("EdgeMlClassifier *cls;")
        temp.append("")
        temp.append("void setup() {")
        temp.append("   Serial.begin(115200);")
        temp.append("   cls = new EdgeMlClassifier();")
        temp.append("}")
        temp.append("")
        temp.append("void loop() {")
        for t in timeseries:
            temp.append(f'   cls->add_datapoint("{t}", get{t}());')
        
        temp.append("   int predicted_class = cls->predict();")
        temp.append("   cls->class_to_label(predicted_class, label);")
        temp.append("   Serial.println(label);")
        temp.append("}")
        return "\n".join(temp)
