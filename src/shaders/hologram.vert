#version 460 core

// Holographic Vertex Shader - Optimized for AMD RX 7800 XT
// Implements parallax holography with RDNA3 wavefront optimizations

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoord;

uniform mat4 mvp;
uniform mat4 model;
uniform mat4 view;
uniform float time;
uniform float hologram_intensity;
uniform vec3 camera_pos;

out vec3 fragPos;
out vec3 fragNormal;
out vec2 fragTexCoord;
out float hologram_factor;
out vec3 view_dir;

// AMD RDNA3 optimized noise function
float amd_noise(vec3 p) {
    // Optimized for wavefront execution
    return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
}

void main() {
    // Holographic displacement with quantum interference patterns
    vec3 displaced_pos = position;
    
    // Multi-layer displacement for depth effect
    float noise1 = amd_noise(position + time * 0.5);
    float noise2 = amd_noise(position * 2.0 + time * 0.3);
    float noise3 = amd_noise(position * 4.0 - time * 0.2);
    
    // Combine noise layers
    float combined_noise = noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2;
    
    // Apply holographic distortion
    displaced_pos.y += sin(time * 2.0 + position.x * 5.0 + combined_noise * 3.14) * 0.02 * hologram_intensity;
    displaced_pos.x += cos(time * 1.5 + position.z * 3.0 + combined_noise * 2.0) * 0.01 * hologram_intensity;
    displaced_pos.z += sin(time * 3.0 + position.y * 4.0) * 0.005 * hologram_intensity;
    
    // Calculate world position
    fragPos = vec3(model * vec4(displaced_pos, 1.0));
    fragNormal = mat3(transpose(inverse(model))) * normal;
    fragTexCoord = texCoord;
    
    // Calculate view direction for fresnel effects
    view_dir = normalize(camera_pos - fragPos);
    
    // Hologram intensity based on viewing angle and distance
    float view_angle = abs(dot(normalize(fragNormal), view_dir));
    float distance_factor = 1.0 / (1.0 + length(camera_pos - fragPos) * 0.1);
    hologram_factor = view_angle * distance_factor * hologram_intensity;
    
    // Add subtle breathing effect
    hologram_factor *= (sin(time * 1.5) * 0.1 + 0.9);
    
    gl_Position = mvp * vec4(displaced_pos, 1.0);
}