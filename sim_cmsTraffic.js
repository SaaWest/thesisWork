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

function randomSleep() {
    sleep(Math.random() * 2 + 1); // 1-3s
}
// K6 options with stages for low → medium → high → cooldown traffic
export const options = {
    stages: [
        { duration: '5m', target: 10 },   // ramp to low traffic
        { duration: '15m', target: 10 },  // hold low baseline
        { duration: '5m', target: 20 },   // ramp to medium traffic
        { duration: '15m', target: 20 },  // hold medium baseline
        { duration: '5m', target: 30 },   // ramp to high traffic
        { duration: '15m', target: 30 },  // hold high baseline
        { duration: '5m', target: 0 },    // cool down
    ],
};


export default function () {
    // Simulate normal browsing
    let res = http.get(`${BASE_URL}${randomEndpoint()}`);
    check(res, { 'status is 200': (r) => r.status === 200 });

    // Optional: occasionally simulate a “form submission” POST (realistic user action)
    if (Math.random() < 0.2) { // 20% chance
        const payload = {
            name: 'k6 Tester',
            email: 'tester@example.com',
            message: 'Testing IDS traffic',
        };
        const params = { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } };
        let postRes = http.post(`${BASE_URL}/index.php?module=Contact&func=submit`, payload, params);
        check(postRes, { 'POST status 200': (r) => r.status === 200 });
    }

    // Random sleep to simulate natural variation
    randomSleep();
}