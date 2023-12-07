
#ifndef FEATURE_EXTRACTOR_HPP
#define FEATURE_EXTRACTOR_HPP
#include <algorithm>
#include <numeric>
#include <cmath>
#include <vector>

using namespace std;

float sum(vector<float>& x) {
    return accumulate(x.begin(), x.end(), 0.0);
}

float in_place_median(vector<float>& x) {
    size_t n = x.size();
    size_t mid = n / 2;
    nth_element(x.begin(), x.begin() + mid, x.end());
    float median = x[mid];
    if (n % 2 == 0) {
        nth_element(x.begin(), x.begin() + mid - 1, x.begin() + mid);
        median = (median + x[mid - 1]) / 2.0;
    }
    return median;
}

float median(vector<float>& x) {
    vector<float> copy_x = x;
    return in_place_median(copy_x);
}

float mean(vector<float>& x) {
    float sum_x = sum(x);
    return sum_x / x.size();
}

float standard_deviation(vector<float>& x) {
    float mean_x = mean(x);
    float sq_sum = 0.0;
    for (float value : x) {
        sq_sum += (value - mean_x) * (value - mean_x);
    }
    float variance = sq_sum / x.size();
    return sqrt(variance);
}

float variance(vector<float>& x) {
    float mean_x = mean(x);
    float sq_sum = 0.0;
    for (float value : x) {
        sq_sum += (value - mean_x) * (value - mean_x);
    }
    return sq_sum / x.size();
}

float max(vector<float>& x) {
    return *max_element(x.begin(), x.end());
}

float abs_max(vector<float>& x) {
    float max_x = max(x);
    return abs(max_x);
}

float min(vector<float>& x) {
    return *min_element(x.begin(), x.end());
}

float abs_min(vector<float>& x) {
    float min_x = min(x);
    return abs(min_x);
}

#endif