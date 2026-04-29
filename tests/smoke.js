'use strict';
const { readFileSync } = require('fs');
const { resolve } = require('path');

const html = readFileSync(resolve(__dirname, '..', 'index.html'), 'utf8');

const checks = [
  ['has DOCTYPE', html.startsWith('<!DOCTYPE html>')],
  ['has title', html.includes('<title>Token Type Calculator</title>')],
  ['has body', html.includes('<body')],
  ['has token types', html.includes('transistor') && html.includes('decorated')],
];

let failed = 0;
for (const [name, pass] of checks) {
  process.stdout.write(`${pass ? 'PASS' : 'FAIL'} ${name}\n`);
  if (!pass) failed++;
}

if (failed > 0) process.exit(1);
process.stdout.write('All checks passed.\n');
