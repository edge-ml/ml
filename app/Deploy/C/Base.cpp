#include <vector>
#include "feature_extractor.cpp"

#define Matrix vector<vector<float> >

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

Matrix mins = {
    {-69997.0, -1144.0, -699.97, 284.2990151231622, 80825.93, 460.0, 460.0, -1473.0, 131.0},
    {-58687.0, -541.5, -586.87, 341.5212864522503, 116636.7891, 584.0, 584.0, -4398.0, 277.0},
    {326974.0, 3325.0, 3269.74, 536.5316769772313, 287866.24040000007, 5678.0, 5678.0, -186.0, 62.0},
    };
Matrix maxs = {
    {59522.0, 184.0, 595.22, 1235.2182551678873, 1525764.1379, 2633.0, 2633.0, -131.0, 1473.0},
    {224953.0, 2337.0, 2249.53, 1238.3044831946625, 1533397.9931, 4571.0, 4571.0, 819.0, 4398.0},
    {419302.0, 4126.5, 4193.02, 1665.3166347274625, 2773279.4939000006, 8140.0, 8140.0, 2202.0, 2202.0},
};

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