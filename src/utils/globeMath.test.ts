import { describe, it, expect } from 'vitest';
import {
    latLonToSphere,
    latLonToFlat,
    latLonToVec3Sphere,
    latLonToVec3Flat,
} from './globeMath';

describe('globeMath', () => {
    it('maps (0,0) to equatorial sphere point of given radius', () => {
        const [x, y, z] = latLonToSphere(0, 0, 5);
        const r = Math.sqrt(x * x + y * y + z * z);
        expect(r).toBeCloseTo(5, 4);
    });

    it('maps poles correctly on sphere', () => {
        const [xN, yN, zN] = latLonToSphere(90, 0, 5);
        const [xS, yS, zS] = latLonToSphere(-90, 0, 5);

        // North pole (0, +R, 0), South pole (0, -R, 0)
        expect(xN).toBeCloseTo(0, 4);
        expect(zN).toBeCloseTo(0, 4);
        expect(yN).toBeCloseTo(5, 4);

        expect(xS).toBeCloseTo(0, 4);
        expect(zS).toBeCloseTo(0, 4);
        expect(yS).toBeCloseTo(-5, 4);
    });

    it('latLonToFlat keeps coordinates inside -10..10 / -5..5 as spec', () => {
        const corners: [number, number][] = [
            [90, -180],
            [90, 180],
            [-90, -180],
            [-90, 180],
            [0, 0],
        ];

        for (const [lat, lon] of corners) {
            const [x, y] = latLonToFlat(lat, lon);
            expect(x).toBeGreaterThanOrEqual(-10 - 1e-6);
            expect(x).toBeLessThanOrEqual(10 + 1e-6);
            expect(y).toBeGreaterThanOrEqual(-5 - 1e-6);
            expect(y).toBeLessThanOrEqual(5 + 1e-6);
        }
    });

    it('Raipur (21.25, 81.63) is mapped inside central region of flat projection', () => {
        const [x, y] = latLonToFlat(21.25, 81.63);
        // Not near extreme edges
        expect(Math.abs(x)).toBeLessThan(10);
        expect(Math.abs(y)).toBeLessThan(5);
    });

    it('vector helpers wrap scalar helpers correctly', () => {
        const vecSphere = latLonToVec3Sphere(10, 20, 5);
        const [x, y, z] = latLonToSphere(10, 20, 5);
        expect(vecSphere.x).toBeCloseTo(x, 4);
        expect(vecSphere.y).toBeCloseTo(y, 4);
        expect(vecSphere.z).toBeCloseTo(z, 4);

        const vecFlat = latLonToVec3Flat(10, 20);
        const [fx, fy] = latLonToFlat(10, 20);
        expect(vecFlat.x).toBeCloseTo(fx, 4);
        expect(vecFlat.y).toBeCloseTo(fy, 4);
        expect(vecFlat.z).toBe(0);
    });
});
