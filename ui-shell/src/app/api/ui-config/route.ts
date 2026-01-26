import { NextResponse } from 'next/server';

/**
 * UI Configuration API
 * 
 * Proxies to the backend to fetch module registry configurations.
 * The shell is plugin-agnostic - it doesn't know about specific modules.
 * The backend discovers installed modules and provides their UI configs.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET() {
    try {
        // Fetch module configurations from the backend
        const response = await fetch(`${BACKEND_URL}/api/ui-config`, {
            headers: {
                'Accept': 'application/json',
            },
            // Don't cache during development
            cache: 'no-store',
        });

        if (!response.ok) {
            throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Transform backend response format to frontend format if needed
        // Backend returns: { "module_name": { config }, ... }
        // Frontend expects: { modules: [{ config }, ...] }
        let modules = data.modules;

        // If backend returns object keyed by module name, convert to array
        if (!Array.isArray(modules) && typeof data === 'object') {
            modules = Object.values(data).filter(
                (item): item is Record<string, unknown> =>
                    typeof item === 'object' && item !== null && 'moduleId' in item
            );
        }

        return NextResponse.json({
            modules: modules || [],
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        console.error('Error loading UI config from backend:', error);

        // Return empty modules array so the app still works
        return NextResponse.json({
            modules: [],
            timestamp: new Date().toISOString(),
            error: {
                message: error instanceof Error ? error.message : 'Failed to load UI configuration',
                code: 'UI_CONFIG_ERROR'
            }
        });
    }
}
