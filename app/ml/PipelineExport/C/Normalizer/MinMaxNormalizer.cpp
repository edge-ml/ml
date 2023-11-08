Matrix mins = {{min}}
Matrix maxs = {{max}}

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