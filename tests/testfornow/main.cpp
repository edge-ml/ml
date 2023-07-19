#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "model.hpp"

const std::string csv_file_path = "./example_data.csv";
const int data_points_to_read = 300; // Number of data points to read from the CSV file

int main() {
    std::ifstream file(csv_file_path);
    if (!file) {
        std::cerr << "Error opening file: " << csv_file_path << std::endl;
        return 1;
    }

    std::string line;
    int data_count = 0;

    // Loop through the CSV file and read time-series sensor data
    while (std::getline(file, line) && data_count < data_points_to_read) {
        std::stringstream ss(line);
        std::string x_str, y_str, z_str;

        if (std::getline(ss, x_str, ',') &&
            std::getline(ss, y_str, ',') &&
            std::getline(ss, z_str, ',')) {

            // Convert the sensor data from strings to floating-point values
            float x = std::stof(x_str);
            float y = std::stof(y_str);
            float z = std::stof(z_str);

            // Add the data points to the model
            add_datapoint(x, y, z);
            data_count++;
        }
    }

    file.close();

    // Perform predictions using the collected data points
    for (int i = 0; i < data_count; i++) {
        int prediction = predict();
        std::cout << "Prediction " << i + 1 << ": " << class_to_label(prediction) << std::endl;
    }

    return 0;
}