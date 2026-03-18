const fs = require('fs');
const { execSync } = require('child_process');

console.log('Getting latest version...');
const versionData = execSync('curl -sL https://api.github.com/repos/koyeb/koyeb-cli/releases/latest').toString();
const tag = JSON.parse(versionData).tag_name;
const version = tag.slice(1);
console.log('Version:', version);

const target = 'linux_amd64';
const url = `https://github.com/koyeb/koyeb-cli/releases/download/${tag}/koyeb-cli_${version}_${target}.tar.gz`;

console.log('Downloading from:', url);
execSync(`curl -fSL -o /tmp/koyeb.tar.gz "${url}"`, { stdio: 'inherit' });

console.log('Extracting...');
execSync('mkdir -p ~/.koyeb/bin');
execSync('tar xf /tmp/koyeb.tar.gz -C ~/.koyeb/bin');
execSync('chmod +x ~/.koyeb/bin/koyeb');
console.log('Done! Koyeb CLI installed to ~/.koyeb/bin/koyeb');
