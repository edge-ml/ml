void extract_features(Matrix &inputs, Matrix &outputs)
{

    for (int i = 0; i < {{num_sensors}}; i++)
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