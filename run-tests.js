const { execSync } = require('child_process');
try {
  const result = execSync('/root/.openclaw/workspace/MasterDataCleaner/node_modules/.bin/playwright test --reporter=line', {
    cwd: '/root/.openclaw/workspace/MasterDataCleaner',
    stdio: 'inherit'
  });
} catch (e) {
  console.log('Exit code:', e.status);
}
