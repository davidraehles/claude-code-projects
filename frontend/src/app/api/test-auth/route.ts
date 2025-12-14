import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json({ error: 'Missing credentials' }, { status: 400 });
    }

    const rawUrl = (process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || '').trim();
    // Validate URL - if it's not meal-planner.up.railway.app, use the correct one
    const backendUrl = (rawUrl && rawUrl.includes('meal-planner.up.railway.app'))
      ? rawUrl
      : 'https://meal-planner.up.railway.app';

    console.log('Test auth - backend URL:', backendUrl);

    // Call backend login endpoint
    const loginRes = await fetch(`${backendUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const responseText = await loginRes.text();
    console.log('Backend response status:', loginRes.status);
    console.log('Backend response:', responseText);

    let data;
    try {
      data = JSON.parse(responseText);
    } catch {
      data = { detail: responseText };
    }

    return NextResponse.json({
      success: loginRes.ok,
      status: loginRes.status,
      statusText: loginRes.statusText,
      backendUrl,
      response: data,
    });
  } catch (error) {
    console.error('Test auth error:', error);
    return NextResponse.json({
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
    }, { status: 500 });
  }
}
