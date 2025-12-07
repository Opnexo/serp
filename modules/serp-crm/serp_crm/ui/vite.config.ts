import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// Path to ui-shell for resolving @ imports
const uiShellSrc = resolve(__dirname, '../../../../ui-shell/src');

/**
 * Vite configuration for building CRM module UI bundle
 *
 * This creates a single JavaScript bundle that:
 * 1. Exports all module components
 * 2. Can be loaded dynamically at runtime by the shell
 * 3. Registers components into a global registry
 */
export default defineConfig({
    plugins: [react()],

    define: {
        // Prevent issues with process.env in browser
        'process.env.NODE_ENV': JSON.stringify('production'),
        'process.env.NEXT_PUBLIC_API_URL': JSON.stringify('http://localhost:8000'),
    },

    build: {
        // Output as a library
        lib: {
            entry: resolve(__dirname, 'bundle-entry.tsx'),
            name: 'SerpCrmModule',
            fileName: 'crm-module',
            formats: ['iife'], // Immediately Invoked Function Expression - works in browser
        },

        // Output directory - this will be served by the backend
        outDir: resolve(__dirname, 'dist'),

        // Externalize dependencies provided by the shell
        rollupOptions: {
            // Use function to handle resolved paths
            external: (id) => {
                // React and related
                if (id === 'react' || id === 'react-dom' || id === 'react/jsx-runtime') {
                    return true;
                }
                // Next.js
                if (id.startsWith('next/')) {
                    return true;
                }
                // Lucide icons
                if (id === 'lucide-react') {
                    return true;
                }
                // Shell UI components (check both alias and resolved path)
                if (id === '@/components/ui' || id.includes('ui-shell/src/components/ui')) {
                    return true;
                }
                return false;
            },
            output: {
                // Global variables for externals
                globals: (id) => {
                    if (id === 'react') return 'React';
                    if (id === 'react-dom') return 'ReactDOM';
                    if (id === 'react/jsx-runtime') return 'ReactJSXRuntime';
                    if (id === 'next/navigation') return 'NextNavigation';
                    if (id === 'next/link') return 'NextLink';
                    if (id === 'next/image') return 'NextImage';
                    if (id === 'next/router') return 'NextRouter';
                    if (id === 'lucide-react') return 'LucideReact';
                    if (id === '@/components/ui' || id.includes('ui-shell/src/components/ui')) {
                        return 'SerpUI';
                    }
                    return id;
                },
                // Ensure the bundle self-registers
                // Note: SerpCrmModule is the local variable created by the IIFE,
                // NOT window.SerpCrmModule. The footer runs in the same scope as the IIFE.
                footer: `
                    // Auto-register module when loaded
                    if (typeof window !== 'undefined' && window.__SERP_MODULE_REGISTRY__ && typeof SerpCrmModule !== 'undefined') {
                        window.__SERP_MODULE_REGISTRY__.register('crm', SerpCrmModule);
                    }
                `,
            },
        },

        // Generate sourcemaps for debugging
        sourcemap: true,

        // Don't minify during development
        minify: false,
    },

    resolve: {
        alias: {
            // Allow importing from shell's components
            '@': uiShellSrc,
        },
    },
});
