void {{name}}({{timeSeriesInput}})
    {
        int window_size = {{output_shape[1]}};

        {% for ts in timeSeries %}
            step_{{step}}_output[{{loop.index-1}}][ctr] = {{ts}};
        {% endfor %}
        ctr++;
        if (ctr >= window_size)
        {
            ctr = 0;
        }
    }