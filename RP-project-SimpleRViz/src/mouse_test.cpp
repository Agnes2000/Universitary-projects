#include <opencv2/opencv.hpp>
#include <iostream>

// TN: Callback chiamata ad ogni evento mouse
void mouseCallback(int event, int x, int y, int flags, void* userdata) {
    if (event == cv::EVENT_LBUTTONDOWN) {
        std::cout << "Left click at: (" << x << ", " << y << ")" << std::endl;
    }
    else if (event == cv::EVENT_RBUTTONDOWN) {
        std::cout << "Right click at: (" << x << ", " << y << ")" << std::endl;
    }
    else if (event == cv::EVENT_MOUSEMOVE) {
        // TN: Stampa solo ogni 50 pixel per non spammare
        if (x % 50 == 0 && y % 50 == 0) {
            std::cout << "Mouse at: (" << x << ", " << y << ")" << std::endl;
        }
    }
}

int main() {
    cv::Mat image = cv::Mat::zeros(600, 800, CV_8UC3);
    image.setTo(cv::Scalar(100, 100, 100));
    
    cv::putText(image, "Click me! Left=initialpose, Right=goal", 
                cv::Point(50, 300),
                cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255, 255, 255), 2);
    
    // TN: Registra callback mouse
    cv::namedWindow("Mouse Test");
    cv::setMouseCallback("Mouse Test", mouseCallback, nullptr);
    
    while (true) {
        cv::imshow("Mouse Test", image);
        int key = cv::waitKey(30);
        if (key == 'q' || key == 27) break;  // q o ESC per uscire
    }
    
    return 0;
}
