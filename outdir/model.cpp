#include <vector>
#include <string>

    #include "feature_extractor.hpp"


#define Matrix vector<vector<float> >

float get_sampling_rate() {
    return 23.168639053254438;
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


    Matrix raw_data(3, vector<float>(20));

    int ctr = 0;

    Matrix features(3, std::vector<float>(9));



int predict(Matrix &features) {
    int num_sensors = features.size();
    int num_features = features[0].size();
    
    if (features[12 / num_features][12 % num_features] <= 0.08294957783073187) {
        
            
    return 0;

        
    }
    else {
        
            
    return 1;

        
    }

}



        void extract_features(Matrix &inputs, Matrix &outputs)
        {

            for (int i = 0; i < 3; i++)
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
    {-632.0000076293945, -31.600000381469727, -31.600000381469727, 0.0, 0.0, -31.600000381469727, 0.0, -78.4000015258789, 0.0},
    {-685.8999910354614, -33.70000076293945, -34.294999551773074, 0.057227656956237945, 0.003275004720700849, -20.0, 0.20000000298023224, -72.0999984741211, 3.5},
    {-520.0000190734863, -26.000000953674316, -26.000000953674316, 0.1465434578116232, 0.02147498502738699, -11.100000381469727, 8.800000190734863, -75.5999984741211, 6.800000190734863},
};
        Matrix maxs = {
    {395.99998474121094, 19.799999237060547, 19.799999237060547, 30.51205663712726, 930.9856002272616, 44.0, 44.0, 19.799999237060547, 78.4000015258789},
    {92.49999856948853, 4.699999809265137, 4.624999928474426, 21.144087791595215, 447.0724485386859, 15.899999618530273, 20.0, 4.400000095367432, 72.0999984741211},
    {993.0000305175781, 49.650001525878906, 49.650001525878906, 41.4136978213715, 1715.0943672398705, 78.4000015258789, 78.4000015258789, 21.0, 75.5999984741211},
};

        void normalize(Matrix &input)
        {
            int num_sensors = input.size();
            int feature_size = input[0].size();
            for (int i = 0; i < num_sensors; i++)
            {
                for (int j = 0; j < feature_size; j++)
                {
                    input[i][j] = (input[i][j] - mins[i][j]) / (maxs[i][j] - mins[i][j]);
                }
            }
        }
        

extern "C" {


        void add_datapoint(float x,float y,float z)
            {
                
                    raw_data[0][ctr] = x;
                
                    raw_data[1][ctr] = y;
                
                    raw_data[2][ctr] = z;
                
                ctr++;
                if (ctr >= 20)
                {
                    ctr = 0;
                }
            }
        

int predict() {
    extract_features(raw_data, features);
    normalize(features);
    return predict(features);
}

}