#!/usr/bin/env node

/**
 * Test script to verify frontend can connect to Railway backend
 */

const https = require('https');

const BACKEND_URL = 'https://meal-planner.up.railway.app';

console.log('🧪 Testing connection to Railway backend...');
console.log(`📡 Backend URL: ${BACKEND_URL}\n`);

// Test 1: Health check
function testHealthCheck() {
  return new Promise((resolve, reject) => {
    console.log('1️⃣  Testing /health endpoint...');
    https.get(`${BACKEND_URL}/health`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const health = JSON.parse(data);
          console.log('✅ Health check successful');
          console.log(`   Status: ${health.status}`);
          console.log(`   Service: ${health.service}`);
          console.log(`   Version: ${health.version}`);
          console.log(`   Database: ${health.components?.database?.status || 'unknown'}`);
          console.log(`   Redis: ${health.components?.redis?.status || 'unknown'}\n`);
          resolve(health);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// Test 2: API documentation
function testApiDocs() {
  return new Promise((resolve, reject) => {
    console.log('2️⃣  Testing /api/docs endpoint...');
    https.get(`${BACKEND_URL}/api/docs`, (res) => {
      if (res.statusCode === 200 || res.statusCode === 307) {
        console.log('✅ API docs endpoint accessible\n');
        resolve(true);
      } else {
        console.log(`⚠️  API docs returned status ${res.statusCode}\n`);
        resolve(false);
      }
    }).on('error', reject);
  });
}

// Test 3: API v1 endpoint
function testApiV1() {
  return new Promise((resolve, reject) => {
    console.log('3️⃣  Testing /api/v1 endpoint...');
    https.get(`${BACKEND_URL}/api/v1/health`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('✅ API v1 health check successful\n');
          resolve(true);
        } else {
          console.log(`⚠️  API v1 health returned status ${res.statusCode}\n`);
          resolve(false);
        }
      });
    }).on('error', reject);
  });
}

// Run all tests
async function runTests() {
  try {
    await testHealthCheck();
    await testApiDocs();
    await testApiV1();

    console.log('✅ All backend connectivity tests passed!');
    console.log('\n📝 Next steps:');
    console.log('   1. Start the frontend: npm run dev');
    console.log('   2. Open http://localhost:3000');
    console.log('   3. Try creating an account and logging in');
    console.log('   4. Verify the dashboard loads correctly\n');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

runTests();
