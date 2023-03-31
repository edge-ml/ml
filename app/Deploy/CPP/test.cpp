#include "example.cpp"
#include <iostream>

int main() {
    for (int i = 0; i < 100; i++) {
        add_datapoint(2.34, 1.23, 4.5);
    }
    std::cout << "Added datapoints" << std::endl;
    std::cout << predict();
    

    std::cout << "Complete" << std::endl;
    return 0;
}