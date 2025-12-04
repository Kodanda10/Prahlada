export default `
attribute vec3 aPosSphere;
attribute vec3 aPosFlat;
uniform float uMorph;
uniform float uSize;
uniform float uTime;

void main() {
    vec3 finalPos = mix(aPosSphere, aPosFlat, uMorph);

    vec4 mvPosition = modelViewMatrix * vec4(finalPos, 1.0);
    gl_Position = projectionMatrix * mvPosition;

    gl_PointSize = uSize * (300.0 / -mvPosition.z);
}
`;
