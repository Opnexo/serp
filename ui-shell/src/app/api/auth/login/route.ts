import { NextRequest, NextResponse } from 'next/server';

/**
 * Mock login API endpoint for development
 * TODO: Replace with real backend API when available
 */
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { username, password } = body;

        // Mock authentication - accept testuser/testpass123
        if (username === 'testuser' && password === 'testpass123') {
            return NextResponse.json({
                data: {
                    accessToken: 'mock-jwt-token-' + Date.now(),
                    refreshToken: 'mock-refresh-token-' + Date.now(),
                    tokenType: 'bearer',
                    expiresIn: 3600,
                    user: {
                        id: '1',
                        username: 'testuser',
                        email: 'test@example.com',
                        fullName: 'Test User',
                        isActive: true,
                        isSuperuser: true,
                        roles: ['admin'],
                        permissions: [
                            'users.view',
                            'users.create',
                            'users.update',
                            'users.delete',
                            'crm.view',
                            'crm.create',
                            'crm.update',
                        ],
                        tenantId: null,
                        avatarUrl: null,
                        lastLogin: new Date().toISOString(),
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString(),
                    },
                },
            });
        }

        // Invalid credentials
        return NextResponse.json(
            {
                error: {
                    message: 'Invalid username or password',
                    code: 'INVALID_CREDENTIALS',
                },
            },
            { status: 401 }
        );
    } catch (error) {
        return NextResponse.json(
            {
                error: {
                    message: 'Internal server error',
                    code: 'INTERNAL_ERROR',
                },
            },
            { status: 500 }
        );
    }
}
