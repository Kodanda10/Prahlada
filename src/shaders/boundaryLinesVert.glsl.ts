export default `
uniform float uMorph;
attribute vec3 aPosSphere;
attribute vec3 aPosFlat;
varying vec2 vUv;

void main() {
    vUv = uv;
    vec3 finalPos = mix(aPosSphere, aPosFlat, uMorph);
    vec4 mvPosition = modelViewMatrix * vec4(finalPos, 1.0);
    gl_Position = projectionMatrix * mvPosition;
}
`;
