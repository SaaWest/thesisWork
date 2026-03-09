import http from 'k6/http';
import { sleep, check } from 'k6';

// Base URL of your CMS container
const BASE_URL = 'http://172.18.0.3';

// List of CMS endpoints to simulate realistic traffic
const ENDPOINTS = [
    '/',
    '/admin',
    //'/articles',
    '/index.php?page=how-cmsms-works',
    //'/index.php?page=menu-manager',
    '/index.php?page=minimal-template',
];

// Function to pick a random endpoint
function randomEndpoint() {
    return ENDPOINTS[Math.floor(Math.random() * ENDPOINTS.length)];
}

// K6 options with stages for low → medium → high → cooldown traffic
export const options = {
    stages: [
        //{ duration: '3m', target: 10 },   // Low traffic
        //{ duration: '3m', target: 20 },  // Medium traffic
        { duration: '3m', target: 27 },  // High traffic
        //{ duration: '1m', target: 1 },   // Cooldown
    ],
    thresholds: {
        http_req_failed: ['rate<0.01'], // Fail rate should be <1%
        http_req_duration: ['p(95)<500'], // 95% of requests < 500ms
    },
};

export default function () {
    for (let i = 0; i < 2; i++) {  // Send 2 requests per VU per loop
        const res = http.get(`${BASE_URL}${randomEndpoint()}`);
        check(res, { 'status is 200': (r) => r.status === 200 });
        sleep(Math.random() * 2 + 1);  // 1-3 sec
        //sleep(.3)
    }
}