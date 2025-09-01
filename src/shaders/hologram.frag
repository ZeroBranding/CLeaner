#version 460 core

// Holographic Fragment Shader - RDNA3 Optimized
// Quantum dot glow with parallax holography effects

in vec3 fragPos;
in vec3 fragNormal;
in vec2 fragTexCoord;
in float hologram_factor;
in vec3 view_dir;

uniform float time;
uniform vec3 camera_pos;
uniform sampler2D noise_texture;
uniform float glow_radius;
uniform float hologram_intensity;

out vec4 fragColor;

// AMD RDNA3 optimized quantum dot glow
vec3 quantum_glow(vec2 uv, float intensity, float time_offset) {
    // Quantum color palette
    vec3 cyan = vec3(0.0, 1.0, 1.0);
    vec3 magenta = vec3(1.0, 0.0, 1.0);
    vec3 yellow = vec3(1.0, 1.0, 0.0);
    vec3 blue = vec3(0.2, 0.4, 1.0);
    
    // Multi-octave noise for quantum interference
    float noise1 = texture(noise_texture, uv + time * 0.1 + time_offset).r;
    float noise2 = texture(noise_texture, uv * 2.0 + time * 0.05).g;
    float noise3 = texture(noise_texture, uv * 4.0 - time * 0.03).b;
    
    // Quantum interference pattern
    float interference = sin(time * 3.0 + noise1 * 10.0) * 0.5 + 0.5;
    interference *= cos(time * 2.0 + noise2 * 8.0) * 0.5 + 0.5;
    
    // Color cycling based on quantum states
    vec3 color1 = mix(cyan, magenta, interference);
    vec3 color2 = mix(magenta, yellow, noise2);
    vec3 color3 = mix(yellow, blue, noise3);
    
    // Combine quantum layers
    vec3 final_color = mix(mix(color1, color2, intensity), color3, noise3 * 0.3);
    
    // Apply quantum glow intensity
    float glow = (interference + noise2 + noise3) / 3.0;
    return final_color * glow * intensity;
}

// Parallax holography with depth layers
vec3 parallax_holography(vec2 uv, vec3 view_direction) {
    float depth_scale = 0.05;
    
    // Multiple parallax layers for depth illusion
    vec2 parallax_uv1 = uv + view_direction.xy * depth_scale;
    vec2 parallax_uv2 = uv + view_direction.xy * depth_scale * 2.0;
    vec2 parallax_uv3 = uv + view_direction.xy * depth_scale * 0.5;
    
    // Sample noise at different depths
    float layer1 = texture(noise_texture, parallax_uv1 + time * 0.02).r;
    float layer2 = texture(noise_texture, parallax_uv2 * 1.5 + time * 0.01).g;
    float layer3 = texture(noise_texture, parallax_uv3 * 3.0 - time * 0.015).b;
    
    // Create depth-based color separation
    vec3 depth_colors = vec3(layer1, layer2, layer3);
    
    // Add chromatic aberration for holographic effect
    float aberration = 0.002;
    depth_colors.r = texture(noise_texture, parallax_uv1 + vec2(aberration, 0)).r;
    depth_colors.g = texture(noise_texture, parallax_uv1).g;
    depth_colors.b = texture(noise_texture, parallax_uv1 - vec2(aberration, 0)).b;
    
    return depth_colors;
}

// Neon scanline effect
float neon_scanlines(vec2 uv, float time) {
    float scanline_density = 800.0;
    float scanline_speed = 10.0;
    
    float scanline = sin(uv.y * scanline_density + time * scanline_speed);
    scanline = scanline * 0.05 + 0.95;  // Subtle effect
    
    // Add horizontal scan
    float h_scan = sin(uv.x * 400.0 + time * 5.0) * 0.02 + 0.98;
    
    return scanline * h_scan;
}

// Fresnel rim lighting
float fresnel_rim(vec3 normal, vec3 view_dir, float power) {
    return pow(1.0 - max(0.0, dot(normal, view_dir)), power);
}

void main() {
    vec3 normal = normalize(fragNormal);
    vec3 view_direction = normalize(view_dir);
    
    // Base quantum glow
    vec3 base_glow = quantum_glow(fragTexCoord, hologram_factor, 0.0);
    
    // Parallax holographic layers
    vec3 parallax_effect = parallax_holography(fragTexCoord, view_direction);
    
    // Fresnel rim lighting for holographic edges
    float rim_intensity = fresnel_rim(normal, view_direction, 2.0);
    vec3 rim_color = vec3(0.0, 1.0, 1.0) * rim_intensity * 2.0;
    
    // Neon scanlines
    float scanline_effect = neon_scanlines(fragTexCoord, time);
    
    // Energy field simulation
    float energy_field = sin(time * 4.0 + length(fragPos) * 2.0) * 0.1 + 0.9;
    energy_field *= cos(time * 3.0 + fragTexCoord.x * 10.0) * 0.05 + 0.95;
    
    // Combine all effects
    vec3 final_color = (base_glow + parallax_effect * 0.5 + rim_color) * scanline_effect * energy_field;
    
    // Add subtle color shifting
    final_color.r += sin(time * 2.0 + fragTexCoord.x * 5.0) * 0.1;
    final_color.g += cos(time * 1.8 + fragTexCoord.y * 4.0) * 0.1;
    final_color.b += sin(time * 2.2 - fragTexCoord.x * 3.0) * 0.1;
    
    // Holographic transparency with depth
    float alpha = hologram_factor * 0.8 + 0.2;
    alpha *= energy_field;
    alpha *= (sin(time * 2.0) * 0.1 + 0.9);  // Subtle pulsing
    
    // Distance-based fade
    float distance = length(camera_pos - fragPos);
    alpha *= 1.0 / (1.0 + distance * 0.1);
    
    // Final output with HDR tone mapping
    final_color = final_color / (final_color + vec3(1.0));  // Simple tone mapping
    final_color = pow(final_color, vec3(1.0/2.2));  // Gamma correction
    
    fragColor = vec4(final_color, alpha);
}