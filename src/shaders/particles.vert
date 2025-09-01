#version 460 core

// Neon Particle Flow Vertex Shader
// Optimized for AMD RX 7800 XT compute units

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 velocity;
layout (location = 2) in float life;
layout (location = 3) in float size;

uniform mat4 mvp;
uniform float time;
uniform vec3 gravity;
uniform vec3 wind_force;
uniform float particle_scale;

out float particle_life;
out float particle_size;
out vec3 particle_color;
out float particle_intensity;

// AMD optimized hash function for particle randomization
float amd_hash(float n) {
    return fract(sin(n) * 43758.5453123);
}

vec3 amd_hash3(vec3 p) {
    p = vec3(dot(p, vec3(127.1, 311.7, 74.7)),
             dot(p, vec3(269.5, 183.3, 246.1)),
             dot(p, vec3(113.5, 271.9, 124.6)));
    return fract(sin(p) * 43758.5453123);
}

void main() {
    // Particle physics simulation
    float particle_time = time + amd_hash(float(gl_VertexID)) * 10.0;
    
    // Advanced physics with multiple forces
    vec3 pos = position;
    pos += velocity * particle_time;
    pos += 0.5 * gravity * particle_time * particle_time;
    pos += wind_force * sin(particle_time * 0.5) * 0.5;
    
    // Neon flow field effect
    vec3 flow_offset = amd_hash3(position) * 2.0 - 1.0;
    pos.x += sin(particle_time * 2.0 + position.y * 0.5 + flow_offset.x) * 0.1;
    pos.y += cos(particle_time * 1.5 + position.z * 0.3 + flow_offset.y) * 0.08;
    pos.z += sin(particle_time * 1.8 + position.x * 0.4 + flow_offset.z) * 0.06;
    
    // Spiral motion for energy flow visualization
    float spiral_radius = 0.05;
    float spiral_speed = 3.0;
    pos.x += cos(particle_time * spiral_speed + position.y * 2.0) * spiral_radius;
    pos.z += sin(particle_time * spiral_speed + position.y * 2.0) * spiral_radius;
    
    // Particle lifecycle management
    particle_life = life;
    
    // Size variation based on life and distance
    float life_factor = smoothstep(0.0, 0.2, life) * smoothstep(1.0, 0.8, life);
    particle_size = size * particle_scale * life_factor;
    
    // Dynamic color based on position and velocity
    float speed = length(velocity);
    float height_factor = (pos.y + 2.0) / 4.0;  // Normalize height
    
    // Color transitions: blue (bottom) -> cyan (middle) -> magenta (top) -> white (fast)
    particle_color.r = mix(0.0, 1.0, height_factor) + speed * 0.2;
    particle_color.g = mix(0.5, 1.0, smoothstep(0.0, 1.0, height_factor));
    particle_color.b = mix(1.0, 0.5, height_factor) + speed * 0.1;
    
    // Intensity based on life and movement
    particle_intensity = life_factor * (1.0 + speed * 0.5);
    
    // Particle pulsing effect
    particle_intensity *= (sin(particle_time * 5.0 + amd_hash(float(gl_VertexID)) * 6.28) * 0.2 + 0.8);
    
    gl_Position = mvp * vec4(pos, 1.0);
    gl_PointSize = particle_size * (1.0 + particle_intensity * 0.5);
}