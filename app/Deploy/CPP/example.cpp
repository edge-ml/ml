#include <vector>

#include "feature_extractor.cpp"

#define Matrix vector<vector<float>>

Matrix raw_data(3, vector<float>(50));

int ctr = 0;

Matrix features(3, std::vector<float>(9));

int predict(Matrix &features)
{
    int num_sensors = features.size();
    int num_features = features[0].size();

    if (features[16 / num_features][16 % num_features] <= 0.42380598187446594)
    {

        return 0;
    }
    else
    {

        if (features[3 / num_features][3 % num_features] <= 0.4797907769680023)
        {

            if (features[2 / num_features][2 % num_features] <= 0.31191056966781616)
            {

                return 1;
            }
            else
            {

                if (features[21 / num_features][21 % num_features] <= 0.19779646396636963)
                {

                    return 1;
                }
                else
                {

                    if (features[5 / num_features][5 % num_features] <= 0.5870949923992157)
                    {

                        if (features[0 / num_features][0 % num_features] <= 0.34975704550743103)
                        {

                            if (features[1 / num_features][1 % num_features] <= 0.2727021127939224)
                            {

                                return 0;
                            }
                            else
                            {

                                return 1;
                            }
                        }
                        else
                        {

                            if (features[22 / num_features][22 % num_features] <= 0.3669077903032303)
                            {

                                if (features[18 / num_features][18 % num_features] <= 0.8082178235054016)
                                {

                                    return 0;
                                }
                                else
                                {

                                    if (features[21 / num_features][21 % num_features] <= 0.4035738855600357)
                                    {

                                        return 0;
                                    }
                                    else
                                    {

                                        return 1;
                                    }
                                }
                            }
                            else
                            {

                                if (features[10 / num_features][10 % num_features] <= 0.43386638164520264)
                                {

                                    return 1;
                                }
                                else
                                {

                                    return 0;
                                }
                            }
                        }
                    }
                    else
                    {

                        if (features[6 / num_features][6 % num_features] <= 0.4879264086484909)
                        {

                            return 1;
                        }
                        else
                        {

                            if (features[23 / num_features][23 % num_features] <= 0.5144856423139572)
                            {

                                if (features[10 / num_features][10 % num_features] <= 0.6696308553218842)
                                {

                                    return 1;
                                }
                                else
                                {

                                    return 0;
                                }
                            }
                            else
                            {

                                if (features[2 / num_features][2 % num_features] <= 0.3997640162706375)
                                {

                                    return 1;
                                }
                                else
                                {

                                    return 0;
                                }
                            }
                        }
                    }
                }
            }
        }
        else
        {

            if (features[7 / num_features][7 % num_features] <= 0.45872218906879425)
            {

                if (features[13 / num_features][13 % num_features] <= 0.4314856380224228)
                {

                    return 1;
                }
                else
                {

                    return 0;
                }
            }
            else
            {

                if (features[18 / num_features][18 % num_features] <= 0.7356633841991425)
                {

                    if (features[4 / num_features][4 % num_features] <= 0.27528733015060425)
                    {

                        return 1;
                    }
                    else
                    {

                        return 0;
                    }
                }
                else
                {

                    return 1;
                }
            }
        }
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
    {-60379.0, -1224.5, -1207.58, 70.26125247958508, 4936.6436, -978.0, 24.0, -1467.0, 74.0},
    {-48746.0, -1032.5, -974.92, 90.02532088251616, 8104.5584, -109.0, 3.0, -4398.0, 55.0},
    {169856.0, 3289.5, 3397.12, 94.80190082482524, 8987.4004, 4067.0, 4067.0, -186.0, 62.0},
};
Matrix maxs = {
    {61244.0, 1484.5, 1224.88, 1337.6851850865362, 1789401.6544000003, 2633.0, 2633.0, -74.0, 1467.0},
    {109856.0, 2313.0, 2197.12, 1425.6674052527117, 2032527.5503999998, 4571.0, 4571.0, 983.0, 4398.0},
    {220356.0, 5268.0, 4407.12, 2313.9128738135323, 5354192.7876, 8140.0, 8140.0, 3805.0, 3805.0},
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

void add_datapoint(float x, float y, float z)
{

    raw_data[0][ctr] = x;

    raw_data[1][ctr] = y;

    raw_data[2][ctr] = z;

    ctr++;
    if (ctr >= 50)
    {
        ctr = 0;
    }
}

int predict()
{
    extract_features(raw_data, features);
    normalize(features);
    return predict(features);
}