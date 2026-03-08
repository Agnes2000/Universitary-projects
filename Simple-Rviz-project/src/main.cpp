#include <memory>
#include <chrono>
#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/occupancy_grid.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "tf2_ros/transform_listener.h"
#include "tf2_ros/buffer.h"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2/LinearMath/Matrix3x3.h"
#include "simple_rviz_clone/visualizer.hpp"
//#include "geometry_msgs/msg/pose_array.hpp" scommenta se non funziona il progetto
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav_msgs/msg/path.hpp"
#include "nav2_msgs/msg/particle_cloud.hpp" // commenta se non funziona il progetto
#include "rclcpp/qos.hpp" //commenta se non funziona

using namespace std::chrono_literals;

class SimpleRVizNode : public rclcpp::Node {
public:
    SimpleRVizNode() : Node("simple_rviz_node") {

        tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
        tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

        visualizer_ = std::make_unique<Visualizer>(800, 800, tf_buffer_);
        
        // TN: Registra callback per eventi mouse
        visualizer_->setInitialPoseCallback(
            std::bind(&SimpleRVizNode::onInitialPoseSet, this,
                     std::placeholders::_1, std::placeholders::_2, std::placeholders::_3));
        
        visualizer_->setGoalCallback(
            std::bind(&SimpleRVizNode::onGoalSet, this,
                     std::placeholders::_1, std::placeholders::_2, std::placeholders::_3));
                     
        // TN: Crea publishers per initialpose e goal
        initial_pose_pub_ = this->create_publisher<geometry_msgs::msg::PoseWithCovarianceStamped>("/initialpose", 10);

        
        goal_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
            "/goal_pose", 10);

        rclcpp::QoS map_qos = rclcpp::QoS(rclcpp::KeepLast(1)).transient_local();
	map_sub_ = this->create_subscription<nav_msgs::msg::OccupancyGrid>(
   	    "/map", map_qos,
    	     
    	     std::bind(&SimpleRVizNode::map_callback, this, std::placeholders::_1));

        scan_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/scan", 10,
            std::bind(&SimpleRVizNode::scan_callback, this, std::placeholders::_1));
/*
	scommenta se il progetto non funziona
        particles_sub_ = this->create_subscription<geometry_msgs::msg::PoseArray>(
            "/particle_cloud", 10,
            std::bind(&SimpleRVizNode::particles_callback, this, std::placeholders::_1));
            */ 
            
        // QoS BEST_EFFORT + VOLATILE (come il publisher!)
        rclcpp::QoS qos_particles(10);
        qos_particles.reliability(rclcpp::ReliabilityPolicy::BestEffort);
        qos_particles.durability(rclcpp::DurabilityPolicy::Volatile);
        
        particles_sub_ = this->create_subscription<nav2_msgs::msg::ParticleCloud>(
            "/particle_cloud",
            qos_particles,  // USA IL QoS CUSTOM!
            std::bind(&SimpleRVizNode::particlesCallback, this, std::placeholders::_1)
        ); //commenta se non funziona il codice
            
        // TN: Sottoscrizione al percorso pianificato
        path_sub_ = this->create_subscription<nav_msgs::msg::Path>(
            "/plan", 10,
            std::bind(&SimpleRVizNode::path_callback, this, std::placeholders::_1));

        update_timer_ = this->create_wall_timer(
            33ms,
            std::bind(&SimpleRVizNode::update_callback, this));
            
        RCLCPP_INFO(this->get_logger(), "Simple RVIZ avviato! Mouse ready.");

        RCLCPP_INFO(this->get_logger(), "Simple RVIZ avviato!");
    }

private:

    void path_callback(const nav_msgs::msg::Path::SharedPtr msg) {
        visualizer_->setPath(msg);
    }

    void map_callback(const nav_msgs::msg::OccupancyGrid::SharedPtr msg) {
        visualizer_->setMap(msg);
    }

    void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) {
        visualizer_->setLaser(msg);
    }

/* Scommenta se non funziona
    void particles_callback(const geometry_msgs::msg::PoseArray::SharedPtr msg) {
        visualizer_->setParticles(msg);
    } */
    
    void particlesCallback(const nav2_msgs::msg::ParticleCloud::SharedPtr msg) {
        std::cout << "*** CALLBACK PARTICELLE CHIAMATA! Ricevute " 
                  << msg->particles.size() << " particelle ***" << std::endl;
        visualizer_->setParticles(msg);
    } //commenta se non funziona

    //void particlesPoseCallback(const geometry_msgs::msg::PoseArray::SharedPtr msg);

    void update_callback() {
        updateRobotPose();
        visualizer_->render();
    }

    void updateRobotPose() {
        try {
            auto transform = tf_buffer_->lookupTransform(
                "map",
                "base_link",
                tf2::TimePointZero);

            double x = transform.transform.translation.x;
            double y = transform.transform.translation.y;

            tf2::Quaternion q(
                transform.transform.rotation.x,
                transform.transform.rotation.y,
                transform.transform.rotation.z,
                transform.transform.rotation.w);

            tf2::Matrix3x3 m(q);
            double roll, pitch, yaw;
            m.getRPY(roll, pitch, yaw);

            visualizer_->setRobotPose(x, y, yaw);

        } catch (const tf2::TransformException& ex) {
            RCLCPP_DEBUG(this->get_logger(), "TF lookup failed: %s", ex.what());
        }
    }
    
    // TN: Chiamato quando utente setta initial pose
    void onInitialPoseSet(double x, double y, double theta) {
        auto msg = geometry_msgs::msg::PoseWithCovarianceStamped();
        
        msg.header.stamp = this->now();
        msg.header.frame_id = "map";
        
        msg.pose.pose.position.x = x;
        msg.pose.pose.position.y = y;
        msg.pose.pose.position.z = 0.0;
        
        // TN: Converti angolo → quaternion
        tf2::Quaternion q;
        q.setRPY(0, 0, theta);
        msg.pose.pose.orientation.x = q.x();
        msg.pose.pose.orientation.y = q.y();
        msg.pose.pose.orientation.z = q.z();
        msg.pose.pose.orientation.w = q.w();
        
        // TN: Covarianza (incertezza) - valori standard
        msg.pose.covariance[0] = 0.25;   // x
        msg.pose.covariance[7] = 0.25;   // y
        msg.pose.covariance[35] = 0.068; // yaw
        
        initial_pose_pub_->publish(msg);
        RCLCPP_INFO(this->get_logger(), "Published initial pose: [%.2f, %.2f, %.2f]", 
                    x, y, theta);
    }
    
    // TN: Chiamato quando utente setta goal
    // TN: Chiamato quando utente setta goal
    void onGoalSet(double x, double y, double theta) {
        auto msg = geometry_msgs::msg::PoseStamped();
        
        msg.header.stamp = this->now();
        msg.header.frame_id = "map";
        
        msg.pose.position.x = x;
        msg.pose.position.y = y;
        msg.pose.position.z = 0.0;
        
        // TN: Quaternion per orientamento
        tf2::Quaternion q;
        q.setRPY(0, 0, theta);
        msg.pose.orientation.x = q.x();
        msg.pose.orientation.y = q.y();
        msg.pose.orientation.z = q.z();
        msg.pose.orientation.w = q.w();
        
        goal_pub_->publish(msg);
        
        // TN: Salva goal per visualizzazione
    	visualizer_->setGoalPose(x, y, theta);
    	
        RCLCPP_INFO(this->get_logger(), "Published goal: [%.2f, %.2f, %.2f]", 
                    x, y, theta);
                    
	}
	
    std::unique_ptr<Visualizer> visualizer_;
    std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener> tf_listener_;

    rclcpp::Subscription<nav_msgs::msg::OccupancyGrid>::SharedPtr map_sub_;
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
    //rclcpp::Subscription<geometry_msgs::msg::PoseArray>::SharedPtr particles_sub_; scommenta se non funziona
    rclcpp::Subscription<nav2_msgs::msg::ParticleCloud>::SharedPtr particles_sub_;// commenta se non funziona

    rclcpp::TimerBase::SharedPtr update_timer_;
    
    // TN: Publishers
    rclcpp::Publisher<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr initial_pose_pub_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr goal_pub_;
    rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr path_sub_;		                 
    
};

// ====================
// CALLBACK DEFINITIONS
// ====================

/* scommenta se non funziona il codice
void SimpleRVizNode::particlesPoseCallback(
    const geometry_msgs::msg::PoseArray::SharedPtr msg)
{
    visualizer_->setParticles(msg);
} */
/*
void SimpleRVizNode::particlesCallback(const nav2_msgs::msg::ParticleCloud::SharedPtr msg) //commenta se non funziona
{
    RCLCPP_INFO(this->get_logger(), "Received %zu particles", msg->particles.size());
    visualizer_->setParticles(msg);
}
*/



int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SimpleRVizNode>());
    rclcpp::shutdown();
    return 0;
}
