export default `
uniform float uTime;
attribute vec3 instanceColor;
attribute mat4 aMatrixSphere;
attribute mat4 aMatrixFlat;
varying vec3 vColor;
uniform float uTime;
uniform float uMorph;

// Helper to mix matrices (linear interpolation of elements)
mat4 mixMat4(mat4 a, mat4 b, float t) {
    return a * (1.0 - t) + b * t;
}

void main() {
    vColor = instanceColor;

    // Pulse effect
    float pulse = 1.0 + 0.3 * sin(uTime * 3.0 + instanceColor.r * 10.0);
    
    vec3 transformed = position;
    transformed.y *= pulse; // Scale height

    // Morph Matrices
    // Note: Linearly interpolating matrices distorts scale/rotation mid-way, 
    // but for a quick morph it's often acceptable or we can decompose.
    // For this constraint, simple mix is efficient and sufficient visually.
    mat4 finalInstanceMatrix = mixMat4(aMatrixSphere, aMatrixFlat, uMorph);

    vec4 mvPosition = modelViewMatrix * finalInstanceMatrix * vec4(transformed, 1.0);
    gl_Position = projectionMatrix * mvPosition;
}
`;
