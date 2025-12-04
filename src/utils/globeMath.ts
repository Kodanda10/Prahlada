import * as THREE from 'three';

export const latLonToSphere = (lat: number, lon: number, radius = 5): [number, number, number] => {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    const x = -radius * Math.sin(phi) * Math.cos(theta);
    const y = radius * Math.cos(phi);
    const z = radius * Math.sin(phi) * Math.sin(theta);
    return [x, y, z];
};

export const latLonToFlat = (lat: number, lon: number): [number, number] => {
    const x = ((lon + 180) / 360) * 20 - 10;
    const y = ((90 - lat) / 180) * 10 - 5;
    return [x, y];
};

export const latLonToVec3Sphere = (lat: number, lon: number, radius = 5) =>
    new THREE.Vector3(...latLonToSphere(lat, lon, radius));

export const latLonToVec3Flat = (lat: number, lon: number) =>
    new THREE.Vector3(latLonToFlat(lat, lon)[0], latLonToFlat(lat, lon)[1], 0);
