#include "simple_rviz_clone/visualizer.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include <iostream>
#include <cmath>

// Variabile globale per callback OpenCV
static Visualizer* global_visualizer_ptr = nullptr;

// Dichiarazione callback OpenCV
void openCVMouseCallback(int event, int x, int y, int flags, void* userdata);

Visualizer::Visualizer(int width, int height, std::shared_ptr<tf2_ros::Buffer> tf_buffer)
: canvas_(),
  width_(width),
  height_(height),
  path_(nullptr),
  path_received_(false),
  map_(nullptr),
  scan_(nullptr),
  map_received_(false),
  scan_received_(false),
  robot_x_(0.0),
  robot_y_(0.0),
  robot_theta_(0.0),
  robot_pose_received_(false),
  scale_(100.0),
  offset_(width_/2.0, height_/2.0),
  particles_(nullptr),
  particles_received_(false),
  tf_buffer_(tf_buffer),
  goal_x_(0.0),
  goal_y_(0.0),
  goal_theta_(0.0),
  goal_received_(false),
  initial_pose_callback_(nullptr),
  goal_callback_(nullptr),
  waiting_for_orientation_(false),
  click_position_()
{
    canvas_ = cv::Mat::zeros(height_, width_, CV_8UC3);

    global_visualizer_ptr = this;
    cv::namedWindow("Simple RVIZ");
    cv::setMouseCallback("Simple RVIZ", openCVMouseCallback, nullptr);

    std::cout << "Visualizer creato: " << width_ << "x" << height_ << std::endl;
}


// Setters


void Visualizer::setPath(const nav_msgs::msg::Path::SharedPtr path) {
    path_ = path;
    path_received_ = true;
}

void Visualizer::drawPath() {
    if (!path_received_ || path_->poses.empty()) return;
    
    // TN: Disegna linea che connette tutti i waypoint
    for (size_t i = 0; i < path_->poses.size() - 1; ++i) {
        double x1 = path_->poses[i].pose.position.x;
        double y1 = path_->poses[i].pose.position.y;
        double x2 = path_->poses[i+1].pose.position.x;
        double y2 = path_->poses[i+1].pose.position.y;
        
        cv::Point p1 = worldToPixel(x1, y1);
        cv::Point p2 = worldToPixel(x2, y2);
        
        // TN: Linea ciano per il percorso
        cv::line(canvas_, p1, p2, cv::Scalar(255, 255, 0), 2);
    }
    
    // TN: Info numero waypoints
    std::string info = "Path waypoints: " + std::to_string(path_->poses.size());
    cv::putText(canvas_, info, cv::Point(10, 150),
                cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(255, 255, 0), 1);
}

void Visualizer::setMap(const nav_msgs::msg::OccupancyGrid::SharedPtr map) {
    map_ = map;
    map_received_ = true;
}

void Visualizer::setLaser(const sensor_msgs::msg::LaserScan::SharedPtr scan) {
    scan_ = scan;
    scan_received_ = true;
}

void Visualizer::setRobotPose(double x, double y, double theta) {
    robot_x_ = x;
    robot_y_ = y;
    robot_theta_ = theta;
    robot_pose_received_ = true;
}

/* scommenta se non funziona
void Visualizer::setParticles(const geometry_msgs::msg::PoseArray::SharedPtr particles) {
    particles_ = particles;
    particles_received_ = true;
} */

void Visualizer::setParticles(const nav2_msgs::msg::ParticleCloud::SharedPtr particles) {
    particles_ = particles;  
    particles_received_ = true;
    // DEBUG: Stampa SEMPRE quando riceve
    std::cout << "=== VISUALIZER: Particelle ricevute: " 
              << particles->particles.size() << " ===" << std::endl;
}


void Visualizer::setGoalPose(double x, double y, double theta) {
    goal_x_ = x;
    goal_y_ = y;
    goal_theta_ = theta;
    goal_received_ = true;
}

void Visualizer::drawGoal() {
    if (!goal_received_) return;
    
    cv::Point goal_pixel = worldToPixel(goal_x_, goal_y_);
    
    // TN: Disegna X grande per il goal
    int size = 15;
    cv::line(canvas_, 
             cv::Point(goal_pixel.x - size, goal_pixel.y - size),
             cv::Point(goal_pixel.x + size, goal_pixel.y + size),
             cv::Scalar(0, 255, 255), 3);  // Giallo
    cv::line(canvas_, 
             cv::Point(goal_pixel.x + size, goal_pixel.y - size),
             cv::Point(goal_pixel.x - size, goal_pixel.y + size),
             cv::Scalar(0, 255, 255), 3);
    
    // TN: Cerchio attorno
    cv::circle(canvas_, goal_pixel, 20, cv::Scalar(0, 255, 255), 2);
    
    // TN: Freccia orientamento goal
    int arrow_len = 25;
    cv::Point arrow_end(
        goal_pixel.x + arrow_len * cos(goal_theta_),
        goal_pixel.y - arrow_len * sin(goal_theta_)
    );
    cv::arrowedLine(canvas_, goal_pixel, arrow_end, 
                    cv::Scalar(0, 255, 255), 2);
}

// Callback mouse
void Visualizer::setInitialPoseCallback(InitialPoseCallback callback) {
    initial_pose_callback_ = callback;
}

void Visualizer::setGoalCallback(GoalCallback callback) {
    goal_callback_ = callback;
}

void Visualizer::pixelToWorld(int px, int py, double& wx, double& wy) {
    wx = (px - offset_.x)/scale_;
    wy = -(py - offset_.y)/scale_;
}

void Visualizer::handleMouseEvent(int event, int x, int y, int flags) {
    (void)flags; // evita warning unused
    if (event == cv::EVENT_LBUTTONDOWN) {
        if (!waiting_for_orientation_) {
            click_position_ = cv::Point(x, y);
            waiting_for_orientation_ = true;
            std::cout << "Initial pose: click again to set orientation" << std::endl;
        } else {
            double x1, y1, x2, y2;
            pixelToWorld(click_position_.x, click_position_.y, x1, y1);
            pixelToWorld(x, y, x2, y2);
            double theta = atan2(y2 - y1, x2 - x1);
            if (initial_pose_callback_) initial_pose_callback_(x1, y1, theta);
            waiting_for_orientation_ = false;
        }
    } else if (event == cv::EVENT_RBUTTONDOWN) {
        double wx, wy;
        pixelToWorld(x, y, wx, wy);
        if (goal_callback_) goal_callback_(wx, wy, 0.0);
    }
}

void Visualizer::adjustScale(double factor) {
    scale_ *= factor;
    // TN: Limiti ragionevoli
    if (scale_ < 5.0) scale_ = 5.0;
    if (scale_ > 300.0) scale_ = 300.0; //Scale aumentata per maggiore chiarezza della mappa e del robot
}

void Visualizer::adjustOffset(double dx, double dy) {
    offset_.x += dx;
    offset_.y += dy;
}

void Visualizer::resetView() {
    scale_ = 20.0;
    offset_ = cv::Point2d(width_ / 2.0, height_ / 2.0);
}

void Visualizer::handleKeyPress(int key) {
    switch(key) {
        case '+':
        case '=':
            adjustScale(1.2);  // Zoom in
            std::cout << "Zoom in: scale=" << scale_ << std::endl;
            break;
        case '-':
        case '_':
            adjustScale(0.8);  // Zoom out
            std::cout << "Zoom out: scale=" << scale_ << std::endl;
            break;
        case 'w':
        case 'W':
            adjustOffset(0, 20);  // Pan su
            break;
        case 's':
        case 'S':
            adjustOffset(0, -20);  // Pan giù
            break;
        case 'a':
        case 'A':
            adjustOffset(20, 0);  // Pan sinistra
            break;
        case 'd':
        case 'D':
            adjustOffset(-20, 0);  // Pan destra
            break;
        case 'r':
        case 'R':
            resetView();
            std::cout << "View reset" << std::endl;
            break;
    }
}

// Conversione world -> pixel
cv::Point Visualizer::worldToPixel(double world_x, double world_y) {
    int px = static_cast<int>(world_x*scale_ + offset_.x);
    int py = static_cast<int>(-world_y*scale_ + offset_.y);
    return cv::Point(px, py);
}

bool Visualizer::transformPoint(const std::string& from_frame,
                                const std::string& to_frame,
                                double in_x, double in_y,
                                double& out_x, double& out_y)
{
    try {
        geometry_msgs::msg::PointStamped point_in;
        point_in.header.frame_id = from_frame;
        point_in.header.stamp = rclcpp::Time(0);
        point_in.point.x = in_x;
        point_in.point.y = in_y;
        point_in.point.z = 0.0;

        geometry_msgs::msg::PointStamped point_out = 
            tf_buffer_->transform(point_in, to_frame, tf2::durationFromSec(0.1));

        out_x = point_out.point.x;
        out_y = point_out.point.y;
        return true;

    } catch (const tf2::TransformException& ex) {
        return false;
    }
    
  }
    
    // Draw Map
void Visualizer::drawMap() {
    if (!map_received_) return;
    double origin_x = map_->info.origin.position.x;
    double origin_y = map_->info.origin.position.y;
    double resolution = map_->info.resolution;

    for (unsigned int y=0; y<map_->info.height; ++y) {
        for (unsigned int x=0; x<map_->info.width; ++x) {
            int idx = y*map_->info.width + x;
            int8_t val = map_->data[idx];
            double wx = origin_x + x*resolution;
            double wy = origin_y + y*resolution;
            cv::Point px = worldToPixel(wx, wy);
            cv::Scalar color = (val==-1 ? cv::Scalar(128,128,128) :
                                val==0 ? cv::Scalar(255,255,255) :
                                cv::Scalar(0,0,0));
            if (px.x>=0 && px.x<width_ && px.y>=0 && px.y<height_)
                cv::circle(canvas_, px, 1, color, -1);
        }
    }
}

// Draw Laser
void Visualizer::drawLaser() {
    if (!scan_received_ || !robot_pose_received_) return;
    double angle = scan_->angle_min;
    for (size_t i=0; i<scan_->ranges.size(); ++i) {
        float r = scan_->ranges[i];
        if (r<scan_->range_min || r>scan_->range_max || std::isnan(r)) {
            angle += scan_->angle_increment;
            continue;
        }
        double lx = r*cos(angle);
        double ly = r*sin(angle);
        double mx, my;
        if (!transformPoint(scan_->header.frame_id, "map", lx, ly, mx, my)) {
            angle += scan_->angle_increment;
            continue;
        }
        cv::Point p = worldToPixel(mx, my);
        if (p.x>=0 && p.x<width_ && p.y>=0 && p.y<height_)
            cv::circle(canvas_, p, 2, cv::Scalar(0,0,255), -1);
        angle += scan_->angle_increment;
    }

    // ROBOT: Cerchio BLU più grande
    cv::Point robot_pixel = worldToPixel(robot_x_, robot_y_);
    cv::circle(canvas_, robot_pixel, 12, cv::Scalar(255, 100, 0), -1);  
    int arrow_len = 25;  // Più lunga
    cv::Point arrow_end(
        robot_pixel.x + arrow_len * cos(robot_theta_),
        robot_pixel.y - arrow_len * sin(robot_theta_)
    );
    cv::arrowedLine(canvas_, robot_pixel, arrow_end, 
                cv::Scalar(255, 255, 255), 3);  // BIANCO
}

// Draw Particles, scommenta se non funziona
/*
void Visualizer::drawParticles() {
    if (!particles_received_) return;
    for (const auto& pose: particles_->poses) {
        double x = pose.position.x;
        double y = pose.position.y;
        cv::Point p = worldToPixel(x,y);
        if (p.x>=0 && p.x<width_ && p.y>=0 && p.y<height_)
            cv::circle(canvas_, p, 1, cv::Scalar(0,255,0), -1);
    }
}
*/

// Draw Particles - DEBUG VERSION
void Visualizer::drawParticles() {
    if (!particles_received_) {
        std::cout << "*** DRAW: Particelle NON ricevute ***" << std::endl;
        return;
    }
    
    std::cout << "*** DRAW: Disegno " << particles_->particles.size() 
              << " particelle ***" << std::endl;
    
    // NOTA: nav2_msgs usa .particles NON .poses!
    for (const auto& particle : particles_->particles) {
        double x = particle.pose.position.x;
        double y = particle.pose.position.y;
        
        cv::Point pixel = worldToPixel(x, y);
        
        if (pixel.x >= 0 && pixel.x < width_ && 
            pixel.y >= 0 && pixel.y < height_) {
            // Particelle VERDI
            cv::circle(canvas_, pixel, 2, cv::Scalar(0, 255, 0), -1);
        }
    }
}



// Render
void Visualizer::render() {
    canvas_.setTo(cv::Scalar(50, 50, 50));
    
    drawMap();
    drawParticles();
    drawPath();
    drawLaser();
    drawGoal();
    
    // TN: Pannello info semi-trasparente
    cv::Mat overlay = canvas_.clone();
    cv::rectangle(overlay, cv::Point(0, 0), cv::Point(350, 200), 
                  cv::Scalar(20, 20, 20), -1);
    cv::addWeighted(overlay, 0.7, canvas_, 0.3, 0, canvas_);
    
    // TN: Titolo
    cv::putText(canvas_, "Simple RVIZ Clone - ROS2", cv::Point(10, 25),
                cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 2);
    
    int y = 55;
    int spacing = 25;
    
    // TN: Info mappa
    if (map_received_) {
        std::string map_info = "Map: " + std::to_string(map_->info.width) + "x" + 
                              std::to_string(map_->info.height) + " @ " +
                              std::to_string(map_->info.resolution) + "m/px";
        cv::putText(canvas_, map_info, cv::Point(10, y),
                    cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(255, 255, 255), 1);
    }
    y += spacing;
    
    // TN: Info robot
    if (robot_pose_received_) {
        char robot_text[150];
        snprintf(robot_text, sizeof(robot_text), 
                "Robot: x=%.2fm y=%.2fm theta=%.1fdeg", 
                robot_x_, robot_y_, robot_theta_ * 180.0 / M_PI);
        cv::putText(canvas_, robot_text, cv::Point(10, y),
                    cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(100, 200, 255), 1);
    }
    y += spacing;
    
    // TN: Info particelle
    if (particles_received_) {
        //std::string part_info = "Particles: " + std::to_string(particles_->poses.size()); scommenta se non funziona
        std::string part_info = "Particles: " + std::to_string(particles_->particles.size()); //commenta se non funziona
        cv::putText(canvas_, part_info, cv::Point(10, y),
                    cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(0, 255, 0), 1);
    }
    y += spacing;
    
    // TN: Info laser
    if (scan_received_) {
        std::string scan_info = "Laser: " + std::to_string(scan_->ranges.size()) + " points";
        cv::putText(canvas_, scan_info, cv::Point(10, y),
                    cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(0, 0, 255), 1);
    }
    y += spacing;
    
    // TN: Info path
    if (path_received_ && !path_->poses.empty()) {
        std::string path_info = "Path: " + std::to_string(path_->poses.size()) + " waypoints";
        cv::putText(canvas_, path_info, cv::Point(10, y),
                    cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(255, 255, 0), 1);
    }
    y += spacing;
    
    // TN: Info goal
    if (goal_received_) {
        char goal_text[150];
        snprintf(goal_text, sizeof(goal_text), 
                "Goal: x=%.2fm y=%.2fm", goal_x_, goal_y_);
        cv::putText(canvas_, goal_text, cv::Point(10, y),
                    cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(0, 255, 255), 1);
    }
    y += spacing;
    
    // TN: Info zoom
    char zoom_text[100];
    snprintf(zoom_text, sizeof(zoom_text), "Zoom: %.1fx (Scale: %.1f px/m)", 
             scale_ / 20.0, scale_);
    cv::putText(canvas_, zoom_text, cv::Point(10, y),
                cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(200, 200, 200), 1);
    
    // TN: Istruzioni in basso
    cv::putText(canvas_, "Left click: Initial Pose (2x) |Right click: Goal", cv::Point(10, height_ - 70), 	 cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(200, 200, 200), 1);
    cv::putText(canvas_, "+/- Zoom | WASD Pan | R Reset | Q Quit", 
            cv::Point(10, height_ - 45),
            cv::FONT_HERSHEY_SIMPLEX, 0.45, cv::Scalar(150, 150, 150), 1);

    if (waiting_for_orientation_) {
	cv::circle(canvas_, click_position_, 10, cv::Scalar(255, 0, 255), 2);
	    cv::putText(canvas_, ">>> Click to set orientation <<<", 
		        cv::Point(width_/2 - 150, height_ - 20),
		        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 0, 255), 2);
	}

	cv::imshow("Simple RVIZ", canvas_);
	int key = cv::waitKey(1);

	if (key != -1) {
	    handleKeyPress(key);
	    if (key == 'q' || key == 'Q' || key == 27) {
		// TN: Segnala a ROS2 di terminare
		std::cout << "User requested quit" << std::endl;
	    }
	    
	    }
}

// OpenCV mouse callback
void openCVMouseCallback(int event, int x, int y, int flags, void* userdata) {
    (void)userdata; // evita warning unused
    if (global_visualizer_ptr)
        global_visualizer_ptr->handleMouseEvent(event, x, y, flags);
}

