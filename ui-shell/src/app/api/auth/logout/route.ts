import { NextRequest, NextResponse } from 'next/server';

/**
 * Mock logout API endpoint for development
 */
export async function POST(request: NextRequest) {
    // Just return success - token removal handled on client
    return new NextResponse(null, { status: 204 });
}
