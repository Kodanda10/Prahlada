import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 20 }, // Ramp up to 20 users
        { duration: '1m', target: 20 },  // Stay at 20 users
        { duration: '30s', target: 0 },  // Ramp down to 0
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    },
};

const BASE_URL = 'http://localhost:8000'; // Adjust if running against a different env

export default function () {
    // 1. Health Check
    const resHealth = http.get(`${BASE_URL}/`);
    check(resHealth, { 'status was 200': (r) => r.status === 200 });

    // 2. Fetch Stats
    const resStats = http.get(`${BASE_URL}/api/stats`);
    check(resStats, {
        'stats status was 200': (r) => r.status === 200,
        'stats duration < 200ms': (r) => r.timings.duration < 200
    });

    // 3. Search Query (simulated load)
    const searchPayload = JSON.stringify({ query: 'Raipur', k: 10 });
    const params = { headers: { 'Content-Type': 'application/json' } };
    const resSearch = http.post(`${BASE_URL}/api/search`, searchPayload, params);

    check(resSearch, {
        'search status was 200': (r) => r.status === 200,
    });

    sleep(1);
}
