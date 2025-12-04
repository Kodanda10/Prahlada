export default `
varying vec3 vColor;
uniform float uTime;
precision highp float;

void main() {
    // Hexagon Shape (SDF)
    vec2 p = abs(gl_PointCoord - vec2(0.5));
    float hex = max(p.x * 0.866 + p.y * 0.5, p.y); // 0.866 is sin(60)
    
    if (hex > 0.45) discard; // Cutout hexagon

    // Indigo Cyberpunk Theme Colors
    vec3 indigo = vec3(0.39, 0.4, 0.95); // #6366f1 (approx)
    vec3 deepPurple = vec3(0.1, 0.0, 0.3);
    vec3 neonAccent = vec3(0.6, 0.2, 1.0); // Brighter purple accent
    
    // Gradient from center
    float dist = length(gl_PointCoord - vec2(0.5));
    vec3 color = mix(indigo, deepPurple, dist * 1.2);
    
    // Hexagon border glow - sharper
    float border = smoothstep(0.45, 0.42, hex);
    float core = smoothstep(0.2, 0.0, dist);
    
    // Add neon pulse to core
    vec3 finalColor = mix(color, neonAccent, core * 0.5);
    
    // Boost alpha for visibility
    gl_FragColor = vec4(finalColor, (border + core) * 1.8);
}
`;
