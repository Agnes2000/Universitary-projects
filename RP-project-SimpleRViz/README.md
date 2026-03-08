# Simple RVIZ Clone - Robot Programming Project

Agnese Chiessi  
**Corso**: Robot Programming - Prof. Giorgio Grisetti

## Descrizione Progetto

Questo progetto implementa un visualizzatore 3D semplificato (clone di RVIZ) per ROS2 che permette di:
- Visualizzare mappe occupancy grid
- Mostrare scansioni laser in tempo reale
- Visualizzare la posizione del robot mobile
- Mostrare particelle di localizzazione (AMCL)
- Impostare posizione iniziale del robot tramite mouse
- Inviare goal di navigazione tramite mouse
- Visualizzare il percorso pianificato

Il sistema è completamente integrato con ROS2 e utilizza TF2 per gestire le trasformazioni tra frame di riferimento.

## Requisiti

- Ubuntu 22.04 LTS
- ROS2 Humble
- OpenCV 4.x
- Pacchetti ROS2:
  - `rclcpp`
  - `sensor_msgs`
  - `nav_msgs`
  - `geometry_msgs`
  - `tf2_ros`
  - `tf2_geometry_msgs`

## Installazione

### 1. Installa dipendenze
```bash
# Dipendenze sistema
sudo apt update
sudo apt install libopencv-dev

# Dipendenze ROS2
sudo apt install ros-humble-tf2-ros \
                 ros-humble-tf2-geometry-msgs \
                 ros-humble-navigation2 \
                 ros-humble-turtlebot3-simulations
```

### 2. Clona e compila
```bash
# Crea workspace (se non esiste)
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clona repository
git clone https://github.com/Agness2049/RP-project-SimpleRViz.git simple_rviz_clone

# Compila
cd ~/ros2_ws
colcon build --packages-select simple_rviz_clone

# Source
source install/setup.bash
```

## Come Eseguire

### Setup Completo con Simulazione

**Terminale 1 - Gazebo Simulator:**
```bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Terminale 2 - Navigation Stack:**
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True
```

Aspetta che RViz2 si apra, poi:
1. Click su "2D Pose Estimate" (toolbar)
2. Click sulla mappa per settare posizione iniziale approssimativa

**Terminale 3 - Simple RVIZ Clone:**
```bash
ros2 run simple_rviz_clone simple_rviz_node
```

**Terminale 4 (opzionale) - Teleop:**
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

## Come Usare

### Visualizzazione
- **Mappa**: Griglia bianca/nera (libero/occupato)
- **Laser**: Punti rossi attorno al robot
- **Robot**: Cerchio blu con freccia verde (orientamento)
- **Particelle**: Punti verdi (localizzazione AMCL)
- **Path**: Linea ciano (percorso pianificato)
- **Goal**: X giallo con cerchio

### Interazione Mouse
- **Click sinistro (2 volte)**: Setta posizione iniziale
  - Primo click: posizione
  - Secondo click: orientamento
- **Click destro**: Setta goal di navigazione

### Controlli Tastiera
- `+` / `-`: Zoom in/out
- `W` `A` `S` `D`: Pan (muovi vista)
- `R`: Reset vista
- `Q` o `ESC`: Esci


## Testing

### Test 1: Localizzazione Base
1. Avvia sistema completo
2. Setta initial pose in RViz2
3. Verifica convergenza particelle nel tuo visualizzatore
4. Muovi robot con teleop
5. Verifica che laser sia allineato con mappa

### Test 2: Navigazione Autonoma
1. Setta initial pose (click sinistro 2x)
2. Setta goal (click destro)
3. Verifica apparizione path ciano
4. Osserva robot navigare verso goal

### Test 3: Kidnapping
1. Robot in navigazione
2. In RViz2, setta pose lontana dalla reale
3. Osserva particelle spargersi e ri-convergere


