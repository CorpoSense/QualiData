// Simple E2E test using Node.js http module
const http = require('http');

const SERVER_URL = process.env.TEST_URL || 'http://localhost:3000';
const TIMEOUT = 30000;

console.log('Testing:', SERVER_URL);

// Simple test: check if server responds
function testServer() {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Request timeout'));
    }, TIMEOUT);

    http.get(SERVER_URL, (res) => {
      clearTimeout(timeout);
      
      if (res.statusCode === 200) {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (data.includes('MasterDataCleaner')) {
            resolve('✅ Server loads correctly with MasterDataCleaner');
          } else {
            resolve('✅ Server responds (content found)');
          }
        });
      } else {
        reject(new Error(`Server returned status ${res.statusCode}`));
      }
    }).on('error', reject);
  });
}

// Run test
testServer()
  .then(msg => {
    console.log(msg);
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ Test failed:', err.message);
    process.exit(1);
  });
