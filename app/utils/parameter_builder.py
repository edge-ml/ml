from DataModels.parameter import Parameter, NumberParameter, SelectionParameter, TextParameter
from typing import List


class ParameterBuilder:
    def __init__(self, parameters : List[Parameter] = []):
        self.parameters = parameters
        return

    def add_number(self, parameter_name, display_name, description, number_min, number_max, value, step_size=1, required=True, log=False, is_advanced=True):
        # TODO: parameter validation

        # self.__validateParameterName(self.parameters, parameter_name)

        self.parameters.append(NumberParameter.model_validate({
            'name': parameter_name,
            'parameter_type': 'number',
            'display_name': display_name,
            'parameter_name': parameter_name,
            'description': description,
            'number_min': number_min,
            'number_max': number_max,
            'value': value,
            'step_size': step_size, # either 'float' or 'int'
            'required': required,
            'log': log,
            'is_advanced': is_advanced
        }))
        return self

    def add_selection(self, parameter_name, display_name, description, options, value, multi_select=False, required=True, is_advanced=True):
        # TODO: parameter validation

        # self.__validateParameterName(self.parameters, parameter_name)

        self.parameters.append(SelectionParameter.model_validate({
            'name': parameter_name,
            'parameter_type': 'selection',
            'display_name': display_name,
            'parameter_name': parameter_name,
            'description': description,
            'options': options,
            'value': value,
            'multi_select': multi_select,
            'required': required,
            'is_advanced': is_advanced
        }))
        return self
    
    def add_text(self,parameter_name, display_name, description, value, required=True, is_advanced=True):
            self.parameters.append(TextParameter.model_validate({
                "name": parameter_name,
                "parameter_name": parameter_name,
                "parameter_type": "text",
                "display_name": display_name,
                "description": description,
                "value": value,
                "required": required,
                "is_advanced": is_advanced
            }))

    def add_boolean(self, parameter_name, display_name, description, value, required=True, is_advanced=True):
        # TODO: parameter validation

        # self.__validateParameterName(self.parameters, parameter_name)
        self.add_selection(parameter_name, display_name, description, ["True", "False"], str(value), False, required, is_advanced)
        return self
    
    def get_value_by_name(self, name):
        for p in self.parameters:
            if p.name == name:
                return p.value
        raise KeyError()


    def __validateParameterName(parameters, parameter_name):
        if parameter_name in parameters:
            raise ValueError("Parameter is already defined")


