# Interactive Cloth Simulation

An interactive **cloth deformation simulation** developed using WebGL.

The project combines physics, advanced rendering, and interactive audio, allowing users to manipulate a virtual cloth in real time and observe how it responds to collisions, external forces, and user interactions.

## Features / Implemented

- **Particle and spring physics:** The cloth is modeled as a grid of points connected by structural, diagonal, and bending springs.
- **3D object collisions:** Spheres and cubes interact with the cloth through collision detection and resolution algorithms.
- **Rendering and shaders:** Phong lighting model and procedural textures (silk, cotton, linen, denim, velvet).
- **Interactive audio:** Procedurally generated sounds react to the cloth’s movement and impacts with objects.

## Objective

Demonstrate how a modular, integrated approach (physics + graphics + audio) can create an immersive and realistic browser-based experience.

## Technologies

- WebGL
- JavaScript
- GLSL shaders
- Procedural audio

## How to Run

1. Clone or download the repository.
2. Open `index.html` in a modern browser (Chrome, Firefox, or Edge).
3. Interact with the cloth using the mouse and observe collisions and audio effects.
