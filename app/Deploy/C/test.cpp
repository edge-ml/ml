#include "Base.cpp"
#include <iostream>

int main() {
    for (int i = 0; i < 100; i++) {
        add_datapoint(2.34, 1.23, 4.5);
    }
    predict();
    

    std::cout << "Complete" << std::endl;
    return 0;
}