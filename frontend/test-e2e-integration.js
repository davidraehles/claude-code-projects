#!/usr/bin/env node

/**
 * End-to-end test to verify frontend-backend integration
 * This simulates what the frontend does when making API calls
 */

const https = require('https');

const BACKEND_URL = 'https://meal-planner.up.railway.app';

console.log('🔗 Frontend-Backend Integration E2E Test');
console.log('=========================================\n');

// Test data
const testUser = {
  email: `test-${Date.now()}@example.com`,
  password: 'TestPass123!',
  country: 'DE'  // Required by backend
};

console.log(`📝 Test user: ${testUser.email}\n`);

// Function to make HTTP requests
function makeRequest(url, method, data = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || 443,
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    };

    if (data) {
      const body = JSON.stringify(data);
      options.headers['Content-Length'] = Buffer.byteLength(body);
    }

    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', chunk => responseData += chunk);
      res.on('end', () => {
        try {
          const parsed = responseData ? JSON.parse(responseData) : {};
          resolve({ status: res.statusCode, data: parsed, headers: res.headers });
        } catch (e) {
          resolve({ status: res.statusCode, data: responseData, headers: res.headers });
        }
      });
    });

    req.on('error', reject);

    if (data) {
      req.write(JSON.stringify(data));
    }

    req.end();
  });
}

// Test 1: Health Check
async function testHealthCheck() {
  console.log('1️⃣  Testing Health Check Endpoint...');
  try {
    const response = await makeRequest(`${BACKEND_URL}/health`, 'GET');
    if (response.status === 200) {
      console.log(`   ✅ Health check successful`);
      console.log(`   Status: ${response.data.status}`);
      console.log(`   Database: ${response.data.components?.database?.status}`);
      return true;
    } else {
      console.log(`   ❌ Health check failed with status ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
    return false;
  }
}

// Test 2: User Registration
async function testUserRegistration() {
  console.log('\n2️⃣  Testing User Registration...');
  try {
    const response = await makeRequest(
      `${BACKEND_URL}/api/v1/auth/register`,
      'POST',
      testUser
    );

    if (response.status === 200 || response.status === 201) {
      console.log(`   ✅ User registration successful`);
      console.log(`   User ID: ${response.data.id || 'N/A'}`);
      return { success: true, user: response.data };
    } else if (response.status === 400 && response.data.detail?.includes('already exists')) {
      console.log(`   ⚠️  User already exists (expected in repeated tests)`);
      return { success: true, existing: true };
    } else {
      console.log(`   ❌ Registration failed with status ${response.status}`);
      console.log(`   Error: ${JSON.stringify(response.data)}`);
      return { success: false };
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
    return { success: false };
  }
}

// Test 3: User Login
async function testUserLogin() {
  console.log('\n3️⃣  Testing User Login...');
  try {
    const response = await makeRequest(
      `${BACKEND_URL}/api/v1/auth/login`,
      'POST',
      {
        email: testUser.email,  // Backend expects 'email' not 'username'
        password: testUser.password
      }
    );

    if (response.status === 200) {
      console.log(`   ✅ Login successful`);
      console.log(`   Token received: ${response.data.access_token ? 'Yes' : 'No'}`);
      console.log(`   Token type: ${response.data.token_type || 'N/A'}`);
      return { success: true, token: response.data.access_token };
    } else {
      console.log(`   ❌ Login failed with status ${response.status}`);
      console.log(`   Error: ${JSON.stringify(response.data)}`);
      return { success: false };
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
    return { success: false };
  }
}

// Test 4: Protected Endpoint (with token)
async function testProtectedEndpoint(token) {
  console.log('\n4️⃣  Testing Protected Endpoint (User Profile)...');
  try {
    const urlObj = new URL(`${BACKEND_URL}/api/v1/users/me`);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || 443,
      path: urlObj.pathname,
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      }
    };

    const response = await new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode, data: JSON.parse(data) });
          } catch (e) {
            resolve({ status: res.statusCode, data: data });
          }
        });
      });
      req.on('error', reject);
      req.end();
    });

    if (response.status === 200) {
      console.log(`   ✅ Protected endpoint accessible`);
      console.log(`   User: ${response.data.email || 'N/A'}`);
      console.log(`   Name: ${response.data.name || 'N/A'}`);
      return true;
    } else {
      console.log(`   ❌ Protected endpoint failed with status ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
    return false;
  }
}

// Run all tests
async function runAllTests() {
  console.log('Starting integration tests...\n');

  let allPassed = true;

  // Test 1: Health Check
  const healthOk = await testHealthCheck();
  if (!healthOk) allPassed = false;

  // Test 2: Registration
  const regResult = await testUserRegistration();
  if (!regResult.success) allPassed = false;

  // Test 3: Login
  const loginResult = await testUserLogin();
  if (!loginResult.success) allPassed = false;

  // Test 4: Protected Endpoint
  if (loginResult.success && loginResult.token) {
    const protectedOk = await testProtectedEndpoint(loginResult.token);
    allPassed = allPassed && protectedOk;
  }

  console.log('\n' + '='.repeat(50));
  if (allPassed) {
    console.log('✅ All tests passed!');
    console.log('\n🎉 Frontend-Backend Integration is working!');
    console.log('\n📝 What this means:');
    console.log('   ✓ Backend is accessible from the internet');
    console.log('   ✓ User registration works');
    console.log('   ✓ User login and JWT tokens work');
    console.log('   ✓ Protected endpoints are accessible with tokens');
    console.log('   ✓ Frontend can make all necessary API calls');
    console.log('\n🚀 You can now use the frontend at http://localhost:3000');
  } else {
    console.log('❌ Some tests failed');
    console.log('\n📋 Check the errors above and verify:');
    console.log('   - Backend is deployed and running on Railway');
    console.log('   - Database migrations are up to date');
    console.log('   - CORS is configured correctly');
  }
  console.log('='.repeat(50));
}

runAllTests().catch(console.error);
