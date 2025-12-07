import { NextRequest, NextResponse } from 'next/server';

/**
 * Mock user info API endpoint for development
 */
export async function GET(request: NextRequest) {
    const authorization = request.headers.get('authorization');

    if (!authorization || !authorization.startsWith('Bearer ')) {
        return NextResponse.json(
            {
                error: {
                    message: 'Unauthorized',
                    code: 'UNAUTHORIZED',
                },
            },
            { status: 401 }
        );
    }

    // Return mock user data
    return NextResponse.json({
        data: {
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
    });
}
