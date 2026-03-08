#ifndef SIMPLE_RVIZ_CLONE_VISUALIZER_HPP
#define SIMPLE_RVIZ_CLONE_VISUALIZER_HPP

#include <opencv2/opencv.hpp>
#include "nav_msgs/msg/occupancy_grid.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "geometry_msgs/msg/point_stamped.hpp"
#include "tf2_ros/buffer.h"
#include "geometry_msgs/msg/pose_array.hpp"
#include <functional>
#include "nav_msgs/msg/path.hpp"

class Visualizer {
public:

    // TN: Tipo per callback quando utente clicca
    using InitialPoseCallback = std::function<void(double x, double y, double theta)>;
    using GoalCallback = std::function<void(double x, double y, double theta)>;
    
    // TN: Costruttore ora accetta puntatore a TF buffer
    Visualizer(int width, int height, std::shared_ptr<tf2_ros::Buffer> tf_buffer);
    
    void setPath(const nav_msgs::msg::Path::SharedPtr path);
    void setMap(const nav_msgs::msg::OccupancyGrid::SharedPtr map);
    void setLaser(const sensor_msgs::msg::LaserScan::SharedPtr scan);
    void setRobotPose(double x, double y, double theta);
    void setParticles(const geometry_msgs::msg::PoseArray::SharedPtr particles);
    void setGoalPose(double x, double y, double theta);
    void render();
    
    cv::Point worldToPixel(double world_x, double world_y);
    
    // TN: Registra callback per eventi utente
    void setInitialPoseCallback(InitialPoseCallback callback);
    void setGoalCallback(GoalCallback callback);
    
    // TN: Metodo per gestire eventi mouse (chiamato da callback OpenCV)
    void handleMouseEvent(int event, int x, int y, int flags);
    
    void handleKeyPress(int key);
    void resetView();
    
private:
    cv::Mat canvas_;
    int width_, height_;
    
    nav_msgs::msg::Path::SharedPtr path_;
    bool path_received_;
    void drawPath();
    
    nav_msgs::msg::OccupancyGrid::SharedPtr map_;
    sensor_msgs::msg::LaserScan::SharedPtr scan_;
    bool map_received_;
    bool scan_received_;
    
    double robot_x_, robot_y_, robot_theta_;
    bool robot_pose_received_;
    
    double scale_;
    cv::Point2d offset_;
    
    geometry_msgs::msg::PoseArray::SharedPtr particles_;
    bool particles_received_;
    
    // TN: Riferimento a TF buffer per trasformazioni
    std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
    
    void drawMap();
    void drawLaser();
    void drawParticles();
    
    double goal_x_, goal_y_, goal_theta_;
    bool goal_received_;
    void drawGoal();
    
    // TN: Nuovo metodo per trasformare punto con TF2
    bool transformPoint(const std::string& from_frame,
                       const std::string& to_frame,
                       double in_x, double in_y,
                       double& out_x, double& out_y);
                       
    // TN: Callback utente
    InitialPoseCallback initial_pose_callback_;
    GoalCallback goal_callback_;
    
    // TN: Stato mouse
    bool waiting_for_orientation_;
    cv::Point click_position_;
    
    // TN: Converti pixel → coordinate mondo
    void pixelToWorld(int pixel_x, int pixel_y, double& world_x, double& world_y);
    
    void adjustScale(double factor);
    void adjustOffset(double dx, double dy);
};

#endif
