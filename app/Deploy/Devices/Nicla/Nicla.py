from app.Deploy.Devices.BaseDevice import BaseDevice, QuantizationLevels
from app.Deploy.Sensors.Accelerometer import Accelerometer
from typing import List
from jinja2 import Template

class Nicla(BaseDevice):

    def __init__(self) -> None:

        sensors = [Accelerometer()]

        super().__init__(sensors)

    @staticmethod
    def get_name():
        return "Nicla Sense ME"
    
    def getSensorParams(self, tsMap, parameters):

        # if anything order sensitive in before_setup or setup is defined 
        # don't use set, set does not preserve the order
        before_setup = set()
        setup = set()
        obtain_values = dict()

        for sensorConf in tsMap:
            sensor = self.sensors[sensorConf.sensor_id]
            before_setup.add(sensor.get_before_setup_code())
            setup.add(sensor.get_setup_code(40))
            obtain_values[sensor.get_obtain_value_code(sensorConf.component_id)] = ""

        return list(before_setup), list(setup), list(obtain_values.keys())
    
    def getQuantizationParams(self, quantization_options):
        if quantization_options.value == QuantizationLevels.NO_QUANT.value or quantization_options.value == QuantizationLevels.DYN_RANGE.value:
            fill_tensor_input = "input->data.f[i] = data_window[i];"
            retrieve_tensor_output = "output->data.f"
            dequantize_output = ""
            quantization_function = ""
            dequantization_function = ""
            
        elif quantization_options.value == QuantizationLevels.INT8.value:
            fill_tensor_input = "input->data.int8[i] = quantize(data_window[i]);"
            retrieve_tensor_output = "dequantized_logits"
            dequantize_output = """
float dequantized_logits[num_classes] = {0.f};
for (int i = 0; i < num_classes; i++) {
    dequantized_logits[i] = dequantize(output->data.int8[i]);
}
"""
            quantization_function = """
inline __attribute__((always_inline)) int8_t quantize(float x) {
    return x / input->params.scale + input->params.zero_point;
}
"""
            dequantization_function = """
inline __attribute__((always_inline)) float dequantize(int8_t x_quantized)  {
    return (x_quantized - output->params.zero_point) * output->params.scale;
}
"""
        else:
            raise NotImplementedError()
        
        return fill_tensor_input, retrieve_tensor_output, dequantize_output, quantization_function, dequantization_function
        
    def deploy(self, tsMap, parameters, is_neural_network):
        before_setup, setup, obtain_values = self.getSensorParams(tsMap, parameters)
               
        data = {"before_setup": before_setup, "setup": setup, "obtain_values": obtain_values}
        data["add_datapoint_vars"] = ", ".join([x.split(" = ")[0].split(" ")[1] for x in obtain_values])
        data["sensor_stream_count"] = len(obtain_values)
        data["sampling_rate"] = parameters[0].value
        
        # parameter[1] is the quantization parameter
        data["fill_tensor_input"], data["retrieve_tensor_output"], data["dequantize_output"], data["quantization_function"], data["dequantization_function"] = self.getQuantizationParams(parameters[1])
        
        if is_neural_network:
            base_path = f"app/Deploy/Devices/Nicla/BaseNN.cpp"
        else:
            base_path = f"app/Deploy/Devices/Nicla/Base.cpp"
        
        with open(base_path, "r") as f:
            base = f.read()

        template = Template(base)
        res = template.render(data)
        return res