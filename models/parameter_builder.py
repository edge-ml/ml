class ParameterBuilder:
    def __init__(self, parameters = {}):
        self.parameters = parameters
        return

    def add_number(self, parameter_name, number_min, number_max, inclusive_min=True, inclusive_max=True, precision='float', required=True):
        # TODO: parameter validation

        self.parameters[parameter_name] = {
            'parameter_type': 'number',
            'number_min': number_min,
            'number_max': number_max,
            'inclusive_min': inclusive_min,
            'inclusive_max': inclusive_max,
            'precision': precision, # either 'float' or 'int'
            'required': required
        }
        return self

    def add_selection(self, parameter_name, options, multi_select=False, required=True):
        # TODO: parameter validation

        self.parameters[parameter_name] = {
            'parameter_type': 'selection',
            'options': options,
            'multi_select': multi_select,
            'required': required
        }
        return self

    def add_boolean(self, parameter_name, required=True):
        # TODO: parameter validation

        self.parameters[parameter_name] = {
            'parameter_type': 'boolean',
            'required': required
        }
        return self
    


