class ParameterBuilder:
    def __init__(self, parameters = {}):
        self.parameters = parameters
        return

    def add_number(self, parameter_name, display_name, description, number_min, number_max, default, step_size=1, required=True, log=False):
        # TODO: parameter validation

        # self.__validateParameterName(self.parameters, parameter_name)

        self.parameters[parameter_name] = {
            'parameter_type': 'number',
            'display_name': display_name,
            'description': description,
            'number_min': number_min,
            'number_max': number_max,
            'default': default,
            'step_size': step_size, # either 'float' or 'int'
            'required': required,
            'log': log
        }
        return self

    def add_selection(self, parameter_name, display_name, description, options, default, multi_select=False, required=True):
        # TODO: parameter validation

        # self.__validateParameterName(self.parameters, parameter_name)

        self.parameters[parameter_name] = {
            'parameter_type': 'selection',
            'display_name': display_name,
            'description': description,
            'options': options,
            'default': default,
            'multi_select': multi_select,
            'required': required
        }
        return self

    def add_boolean(self, parameter_name, display_name, description, default, required=True):
        # TODO: parameter validation

        # self.__validateParameterName(self.parameters, parameter_name)
        self.add_selection(parameter_name, display_name, description, ["True", "False"], str(default), False, required)
        return self
    
    def __validateParameterName(parameters, parameter_name):
        if parameter_name in parameters:
            raise ValueError("Parameter is already defined")


