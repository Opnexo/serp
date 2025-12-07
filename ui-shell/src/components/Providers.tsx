'use client';

import React, { useState } from 'react';
import * as ReactDOM from 'react-dom';
import * as jsxRuntime from 'react/jsx-runtime';
import * as LucideReact from 'lucide-react';
import * as NextNavigation from 'next/navigation';
import NextLink from 'next/link';
import NextImage from 'next/image';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/lib/auth';
import { PermissionProvider } from '@/lib/permissions';
import { ModuleProvider } from '@/lib/modules';
// Import all UI components to expose globally
import * as SerpUI from '@/components/ui';

// Expose dependencies globally for dynamic module bundles
// This allows module bundles to use these libraries without bundling them
if (typeof window !== 'undefined') {
    // React core
    (window as any).React = React;
    (window as any).ReactDOM = ReactDOM;
    (window as any).ReactJSXRuntime = jsxRuntime;

    // Next.js
    (window as any).NextNavigation = NextNavigation;
    (window as any).NextLink = { default: NextLink };
    (window as any).NextImage = { default: NextImage };

    // Icons
    (window as any).LucideReact = LucideReact;

    // Shell UI components
    (window as any).SerpUI = SerpUI;
}

export function Providers({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        staleTime: 60 * 1000, // 1 minute
                        refetchOnWindowFocus: false,
                    },
                },
            })
    );

    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <PermissionProvider>
                    <ModuleProvider>{children}</ModuleProvider>
                </PermissionProvider>
            </AuthProvider>
        </QueryClientProvider>
    );
}
