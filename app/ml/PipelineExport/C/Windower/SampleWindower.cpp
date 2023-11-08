void add_datapoint({{timeSeriesInput}})
    {
        {% for ts in timeSeries %}
            raw_data[{{loop.index-1}}][ctr] = {{ts}};
        {% endfor %}
        ctr++;
        if (ctr >= {{window_size}})
        {
            ctr = 0;
        }
    }