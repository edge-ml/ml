from app.codegen.inference.BasePlatform import BasePlatform
from app.codegen.inference.InferenceFormats import InferenceFormats

class CPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "C"
    
    def supported_formats(self):
        return [InferenceFormats.C, InferenceFormats.C_EMBEDDED]


    def codegen(self, window_size, timeseries, labels, format, scaler, windowing_mode):
        temp = []
        temp.append(f'#include "___DOWNLOADED_MODEL_BASENAME___.h"')
        temp.append("")
        temp.append("void loop() {")
        for t in timeseries:
            temp.append(f'   add_datapoint("{t}", get{t}());')
        
        temp.append("   int predicted_class = predict();")
        temp.append("   const char* label = class_to_label(predicted_class);")
        temp.append('   printf("%c\\n", label);')
        temp.append("}")
        return "\n".join(temp)
