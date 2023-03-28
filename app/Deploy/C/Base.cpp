#include <vector>
#include "feature_extractor.cpp"

#define Matrix vector<vector<float>>

const int num_sensors = 3;
const int window_size = 50;
const int feature_size = 9;

Matrix raw_data(num_sensors, vector<float>(window_size));
int ctr = 0;

Matrix features(num_sensors, vector<float>(feature_size));

void extract_features(Matrix inputs, Matrix outputs)
{

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

Matrix mins = {{1.0, 2.0, 3.0, 3.4, 4.5}, {1.0, 2.0, 3.0, 3.4, 4.5}, {1.0, 2.0, 3.0, 3.4, 4.5}};
Matrix maxs = {{4.5, 5.6, 6.7, 7.7, 8.9}, {4.5, 5.6, 6.7, 7.7, 8.9}, {4.5, 5.6, 6.7, 7.7, 8.9}};

// Normalization is done inplace
void normalize(Matrix input)
{
    for (int i = 0; i < num_sensors; i++)
    {
        for (int j = 0; j < feature_size; j++)
        {
            input[i][j] = (input[i][j] - mins[i][j]) / (maxs[i][j] - mins[i][j]);
        }
    }
}

void add_datapoint(float acc_x, float acc_y, float acc_z)
{

    raw_data[0][ctr] = acc_x;
    raw_data[1][ctr] = acc_y;
    raw_data[2][ctr] = acc_z;
    ctr++;
    if (ctr >= window_size)
    {
        ctr = 0;
    }
}

int predict()
{
    extract_features(raw_data, features);
    normalize(features);
}