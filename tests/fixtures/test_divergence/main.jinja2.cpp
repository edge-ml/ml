#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <chrono>
#include <thread>

#include "model.hpp"
#include "json.hpp"

using json = nlohmann::json;

const std::string CSV_FILE_PATH = "{{ csv_file_path }}";
const int DATAPOINTS_TO_READ = {{ datapoints_to_read }}; // Number of data points to read from the CSV file
const int WINDOW_SIZE = {{ window_size }}; // Window size

int main() {
    std::ifstream file(CSV_FILE_PATH);
    if (!file) {
        std::cerr << "Error opening file: " << CSV_FILE_PATH << std::endl;
        return 1;
    }

    json cpp_json;
    std::string line;
    int data_count = 0;

    // Loop through the CSV file and read time-series sensor data
    while (std::getline(file, line) && data_count < DATAPOINTS_TO_READ) {
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
            if ({{ time_windowing }}) {
                cpp_json["windowed"].push_back(raw_data);
                extract_features(raw_data, features);
                cpp_json["features"].push_back(features);
                normalize(features);
                cpp_json["normalized"].push_back(features);
                int prediction = predict(features);

                cpp_json["predictions"].push_back(prediction);

                std::this_thread::sleep_for(std::chrono::milliseconds({{  time_window_sep_interval }}));
            } else {
                if (data_count >= WINDOW_SIZE) {
                    cpp_json["windowed"].push_back(raw_data);
                    extract_features(raw_data, features);
                    cpp_json["features"].push_back(features);
                    normalize(features);
                    cpp_json["normalized"].push_back(features);
                    int prediction = predict(features);

                    cpp_json["predictions"].push_back(prediction);
                }
            }
        }
    }

    file.close();

    std::cout << cpp_json.dump() << std::endl;

    return 0;
}