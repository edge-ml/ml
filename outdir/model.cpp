#ifndef EDGEMLPIPELINE_HPP
#define EDGEMLPIPELINE_HPP

#ifdef __EMSCRIPTEN__
#include <emscripten/bind.h>
#endif

#include <vector>
#include <string>

    #include "feature_extractor.hpp"


#define Matrix vector<vector<float>>




    int ctr = 0;

    Matrix step_0_output(3, vector<float>(100));

    Matrix step_1_output(3, vector<float>(9));

    Matrix step_2_output(3, vector<float>(9));


float get_sampling_rate() {
    return 25.83;
}

string class_to_label(int cls) {
    
        if (cls == 0) {
            return "noshake";
        }
    
        if (cls == 1) {
            return "shake";
        }
    
    return "";
}



    void add_datapoint(float AccelerometerX,float AccelerometerY,float AccelerometerZ)
    {
        int window_size = 100;

        
            step_0_output[0][ctr] = AccelerometerX;
        
            step_0_output[1][ctr] = AccelerometerY;
        
            step_0_output[2][ctr] = AccelerometerZ;
        
        ctr++;
        if (ctr >= window_size)
        {
            ctr = 0;
        }
    }

    void step_1(Matrix &inputs, Matrix &outputs)
{
    int num_sensors = 3;
    int num_features = 9;

    for (int i = 0; i < num_sensors; i++)
    {
        outputs[i][0] = sum(inputs[i]);
        outputs[i][1] = median(inputs[i]);
        outputs[i][2] = mean(inputs[i]);
        outputs[i][3] = standard_deviation(inputs[i]);
        outputs[i][4] = variance(inputs[i]);
        outputs[i][5] = max(inputs[i]);
        outputs[i][6] = abs_max(inputs[i]);
        outputs[i][7] = min(inputs[i]);
        outputs[i][8] = abs_min(inputs[i]);
    }
}

    Matrix mins = {
    {-3160.0000381469727, -31.600000381469727, -31.600000381469727, 0.0, 0.0, -31.600000381469727, 0.10000000149011612, -78.4000015258789, 0.20000000298023224},
    {-2905.100025653839, -33.70000076293945, -29.05100025653839, 0.11052594725167089, 0.012215985015879137, -20.0, 0.20000000298023224, -72.0999984741211, 3.5999999046325684},
    {-2600.0000953674316, -26.000000953674316, -26.000000953674316, 0.2183826997184024, 0.04769100353629792, -11.100000381469727, 9.100000381469727, -75.5999984741211, 6.800000190734863},
};
Matrix maxs = {
    {1979.9999237060547, 19.799999237060547, 19.799999237060547, 26.671739595529353, 711.3816930517283, 44.0, 44.0, 19.799999237060547, 78.4000015258789},
    {452.7999978065491, 4.5, 4.527999978065491, 21.440398792611315, 459.6907003862087, 15.899999618530273, 20.0, 4.199999809265137, 72.0999984741211},
    {4965.000152587891, 49.650001525878906, 49.650001525878906, 42.030422666234244, 1766.5564295022973, 78.4000015258789, 78.4000015258789, 21.0, 75.5999984741211},
};

void step_2(Matrix &input, Matrix &outputs)
{
    int num_sensors = input.size();
    int feature_size = input[0].size();
    for (int i = 0; i < num_sensors; i++)
    {
        for (int j = 0; j < feature_size; j++)
        {
            outputs[i][j] = (input[i][j] - mins[i][j]) / (maxs[i][j] - mins[i][j]);
        }
    }
}

    
int step_3(Matrix &features) {
    int num_sensors = features.size();
    int num_features = features[0].size();
    
    if (features[17 / num_features][17 % num_features] <= 0.16131386766210198) {
        
            
    return 0;

        
    }
    else {
        
            
    return 1;

        
    }

}



int predict() {
    
        step_1(step_0_output, step_1_output);
    
        step_2(step_1_output, step_2_output);
    
        return step_3(step_2_output);
    
}

#ifdef __EMSCRIPTEN__
EMSCRIPTEN_BINDINGS(my_module) {
    emscripten::function("predict", &predict);
    emscripten::function("add_datapoint", &add_datapoint);
    emscripten::function("class_to_label", &class_to_label);
}
#endif

#endif