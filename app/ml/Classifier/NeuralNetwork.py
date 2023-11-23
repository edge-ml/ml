from app.codegen.inference.InferenceFormats import InferenceFormats
from app.utils.parameter_builder import ParameterBuilder
from app.ml.Classifier import BaseClassififer
from bson.objectid import ObjectId
from app.internal.config import CLASSIFIER_STORE
from app.ml.BaseConfig import Platforms
from app.Deploy.Devices.BaseDevice import QuantizationLevels
import numpy as np
import os

import tensorflow as tf

class NeuralNetwork(BaseClassififer):
    def __init__(self, parameters=[]):
        super().__init__(parameters)
        self.data_id = None
        self.X_train_representative = None
        
    # static methods
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []
        return pb.parameters

    @staticmethod
    def get_name():
        return "Neural Network Classifier"

    @staticmethod
    def get_description():
        return "Abstract wrapper for neural network classifier, not intended for actual use."

    @staticmethod
    def get_platforms():
        return [InferenceFormats.PYTHON, InferenceFormats.JAVASCRIPT, InferenceFormats.CPP, InferenceFormats.C]
    
    @staticmethod
    def bytes_to_c_arr(data):
        return [format(b, '#04x') for b in data]
    
    @staticmethod
    def is_neural_network():
        return True
    
    def fit(self, X_train, y_train):
        raise NotImplementedError()

    def predict(self, X_test):
        raise NotImplementedError()
    
    def get_state(self):
        return {"data_id": self.data_id}

    def restore(self, dict):
        self.data_id = dict.state["data_id"]
        path = f'{CLASSIFIER_STORE}/{self.data_id}/'
        model_path = os.path.join(path, 'tf_model.tf')
        representative_dataset_path = os.path.join(path, 'repr_dataset.npy')
        self.model = tf.saved_model.load(model_path)
        self.X_train_representative = np.load(representative_dataset_path)

    def persist(self):
        self.data_id = ObjectId()
        path = f'{CLASSIFIER_STORE}/{self.data_id}'
        if not os.path.exists(path):
            os.makedirs(path)
        model_path = os.path.join(path, 'tf_model.tf')
        representative_dataset_path = os.path.join(path, 'repr_dataset.npy')
        tf.saved_model.save(self.model, model_path)
        np.save(representative_dataset_path, self.X_train_representative, allow_pickle=False, fix_imports=False)
        return super().persist()
    
    def export(self, platform: Platforms, quantization_level: QuantizationLevels = QuantizationLevels.NO_QUANT):
        if platform == Platforms.C:
            return self.exportC(quantization_level)
    
    def representative_data_gen(self):
        for sample in self.X_train_representative:
            yield [sample.astype(np.float32)]
            
    def exportC(self, quantization_level: QuantizationLevels = QuantizationLevels.NO_QUANT):
        path = f'{CLASSIFIER_STORE}/{self.data_id}/tf_model.tf'
        converter = tf.lite.TFLiteConverter.from_saved_model(path)
        if quantization_level == QuantizationLevels.DYN_RANGE.value:
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
        elif quantization_level == QuantizationLevels.INT8.value:
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.representative_dataset = self.representative_data_gen
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8
        
        tflite_model = converter.convert()
        
        # tflite_model_path = f'{CLASSIFIER_STORE}/{self.data_id}/tf_model.tflite'
        # with open(tflite_model_path, 'wb') as tflite_file:
        #     tflite_file.write(tflite_model)
            
        c_array = self.bytes_to_c_arr(tflite_model)
        array_content = "{}".format(", ".join(c_array))
        converted_model_str = 'alignas(8) const unsigned char g_model[] PROGMEM = {\n\t'
        # pretty printing the bytes
        chunk_size = 6 * 12
        for i in range(0, len(array_content), chunk_size):
            converted_model_str += array_content[i:i + chunk_size]
            if i + chunk_size < len(array_content):
                converted_model_str += "\n\t"

        converted_model_str += "};\n"
        converted_model_str += f"const int g_model_len = sizeof(g_model);"
       
        return converted_model_str