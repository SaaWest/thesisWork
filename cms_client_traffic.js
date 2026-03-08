import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend } from 'k6/metrics';

// Create a trend to track load or resource usage over time (for example, response times)
let responseTimes = new Trend('response_times');

export const options = {
  vus: 10, // Start with 1 virtual user
  duration: '1h', // Run for 1 hour
  // Don't limit the number of VUs, as we're simulating a dynamic increase/decrease
};

export default function () {
  // Simulate a sinusoidal fluctuation in virtual users based on time
  const currentTime = new Date().getSeconds(); // Get current second to simulate the wave
  const sinusoidalFactor = Math.sin(currentTime / 60 * Math.PI * 2); // Sinusoidal wave between -1 and 1
  const numVUs = Math.max(1, Math.floor(sinusoidalFactor * 9 + 10)); // Adjust VUs dynamically between 1 and 10


  group('Homepage visit', function () {
    const res = http.get('http://172.18.0.3');
    check(res, { 'status is 200': (r) => r.status === 200 });
    responseTimes.add(res.timings.duration); // Track the response time
    sleep(1); // Adjust think time dynamically if needed
  });

  group('Login flow', function () {
    const loginRes = http.post('http://172.18.0.3/admin/login.php', {
      username: 'admin',
      password: 'rootroot',
    });
    check(loginRes, { 'login successful': (r) => r.body.includes('id="d41d8cd98f00b204e9800998ecf8427e"') });
    responseTimes.add(loginRes.timings.duration);
    sleep(1);
  });

  group('How page', function () {
    const howRes = http.post('http://172.18.0.3/index.php?page=how-cmsms-works', {});
    check(howRes, { 'status is 200': (r) => r.status === 200 });
    responseTimes.add(howRes.timings.duration);
    sleep(1);
  });

  group('Menu manager', function () {
    const menuManRes = http.post('http://172.18.0.3/index.php?page=menu-manager', {});
    check(menuManRes, { 'status is 200': (r) => r.status === 200 });
    responseTimes.add(menuManRes.timings.duration);
    sleep(1);
  });

  group('template tab', function () {
   // Example: a POST request for login (requires form data/headers)
    const templateRes = http.post('http://172.18.0.3/index.php?page=minimal-template', {});
     //... other form data 
    check( templateRes, { 'status is 200': (r) => r.status === 200 });
    responseTimes.add(templateRes.timings.duration);
    sleep(.5);
    });
    //check(loginRes, {'redirect to dashboard': (r) => r.status === 302 && r.headers['Location'] && r.headers['Location'].includes('dashboard'),}); //sleep(1); //});
}
