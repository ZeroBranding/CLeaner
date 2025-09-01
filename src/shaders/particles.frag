#version 460 core

// Neon Particle Fragment Shader
// Advanced particle rendering with energy field effects

in float particle_life;
in float particle_size;
in vec3 particle_color;
in float particle_intensity;

uniform float time;
uniform vec2 resolution;
uniform float glow_intensity;

out vec4 fragColor;

// Energy field function for particle interactions
float energy_field(vec2 coord, float time_offset) {
    float dist = length(coord - vec2(0.5));
    
    // Multiple energy rings
    float ring1 = abs(sin((dist - time_offset * 0.1) * 20.0)) * 0.5 + 0.5;
    float ring2 = abs(cos((dist - time_offset * 0.15) * 15.0)) * 0.3 + 0.7;
    float ring3 = abs(sin((dist - time_offset * 0.08) * 25.0)) * 0.2 + 0.8;
    
    return ring1 * ring2 * ring3;
}

// Plasma effect for particle cores
float plasma_core(vec2 coord, float time_offset) {
    vec2 center = coord - vec2(0.5);
    float angle = atan(center.y, center.x);
    float radius = length(center);
    
    // Rotating plasma
    float plasma = sin(angle * 4.0 + time_offset * 3.0) * 0.5 + 0.5;
    plasma *= cos(radius * 10.0 - time_offset * 2.0) * 0.5 + 0.5;
    
    // Radial fade
    plasma *= 1.0 - smoothstep(0.0, 0.5, radius);
    
    return plasma;
}

// Neon glow with distance field
float neon_glow(vec2 coord) {
    float dist = length(coord - vec2(0.5));
    
    // Soft circular gradient
    float glow = 1.0 - smoothstep(0.0, 0.5, dist);
    glow = pow(glow, 1.5);
    
    // Inner bright core
    float core = 1.0 - smoothstep(0.0, 0.2, dist);
    core = pow(core, 3.0);
    
    return glow + core * 2.0;
}

void main() {
    vec2 coord = gl_PointCoord;
    
    // Discard pixels outside circle
    float dist_from_center = length(coord - vec2(0.5));
    if (dist_from_center > 0.5) discard;
    
    // Base neon glow
    float glow = neon_glow(coord);
    
    // Energy field interaction
    float energy = energy_field(coord, time + particle_size);
    
    // Plasma core effect
    float plasma = plasma_core(coord, time * 2.0 + particle_size * 3.14);
    
    // Combine effects
    float total_intensity = glow * energy * particle_intensity;
    total_intensity += plasma * 0.5;
    
    // Apply particle color with energy modulation
    vec3 final_color = particle_color * total_intensity;
    
    // Add energy spikes
    float spike = sin(time * 8.0 + particle_size * 10.0) * 0.1 + 0.9;
    final_color *= spike;
    
    // Particle trail effect (brighter in movement direction)
    float trail_effect = smoothstep(0.3, 0.5, dist_from_center);
    final_color += particle_color * trail_effect * 0.3;
    
    // Life-based fade
    float life_fade = smoothstep(0.0, 0.1, particle_life) * smoothstep(1.0, 0.9, particle_life);
    
    // Distance-based alpha for depth
    float alpha = total_intensity * life_fade * glow_intensity;
    
    // Add subtle sparkle effect
    float sparkle = step(0.98, sin(time * 20.0 + particle_size * 50.0));
    alpha += sparkle * 0.5;
    
    // HDR bloom preparation
    if (total_intensity > 1.0) {
        final_color *= total_intensity;  // Overbright for bloom
    }
    
    fragColor = vec4(final_color, alpha);
}