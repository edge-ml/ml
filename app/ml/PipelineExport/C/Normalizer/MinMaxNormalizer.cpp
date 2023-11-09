Matrix mins = {{min}}
Matrix maxs = {{max}}

void {{name}}(Matrix &input, Matrix &outputs)
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