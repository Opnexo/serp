import { defineConfig, ConfigEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { serpHmrPlugin } from './hmr-plugin';

// Path to ui-shell for resolving @ imports
const uiShellSrc = resolve(__dirname, '../../../../ui-shell/src');

// Module configuration
const MODULE_ID = 'dm';
const HMR_PORT = 5174;

/**
 * Vite configuration for building DM module UI bundle
 *
 * This creates a single JavaScript bundle that:
 * 1. Exports all module components
 * 2. Can be loaded dynamically at runtime by the shell
 * 3. Registers components into a global registry
 * 4. Supports HMR in development mode
 */
export default defineConfig(({ mode }: ConfigEnv) => ({
    plugins: [
        react(),
        // Enable HMR plugin in development
        ...(mode === 'development' ? [serpHmrPlugin({ moduleId: MODULE_ID, port: HMR_PORT })] : []),
    ],

    // Dev server configuration for HMR
    server: {
        port: HMR_PORT,
        hmr: {
            port: HMR_PORT,
        },
        cors: true,
        // Allow connections from the UI Shell
        origin: 'http://localhost:3000',
    },

    define: {
        // Prevent issues with process.env in browser
        'process.env.NODE_ENV': JSON.stringify(mode),
        'process.env.NEXT_PUBLIC_API_URL': JSON.stringify('http://localhost:8000'),
    },


    build: {
        // Output as a library
        lib: {
            entry: resolve(__dirname, 'bundle-entry.tsx'),
            name: 'SerpDmModule',
            fileName: 'dm-module',
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
                // React Router
                if (id === 'react-router-dom' || id.startsWith('react-router')) {
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
                // MUI (externalize to shell)
                if (id.startsWith('@mui/')) {
                    return true;
                }
                // dnd-kit (externalize to shell)
                if (id.startsWith('@dnd-kit/')) {
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
                    if (id === 'react-router-dom') return 'ReactRouterDOM';
                    if (id === 'next/navigation') return 'NextNavigation';
                    if (id === 'next/link') return 'NextLink';
                    if (id === 'next/image') return 'NextImage';
                    if (id === 'next/router') return 'NextRouter';
                    if (id === 'lucide-react') return 'LucideReact';
                    if (id.startsWith('@mui/material')) return 'MuiMaterial';
                    if (id.startsWith('@mui/icons-material')) return 'MuiIcons';
                    if (id.startsWith('@dnd-kit/')) return 'DndKit';
                    if (id === '@/components/ui' || id.includes('ui-shell/src/components/ui')) {
                        return 'SerpUI';
                    }
                    return id;
                },
                // Ensure the bundle self-registers
                footer: `
                    // Auto-register module when loaded
                    if (typeof window !== 'undefined' && window.__SERP_MODULE_REGISTRY__ && typeof SerpDmModule !== 'undefined') {
                        window.__SERP_MODULE_REGISTRY__.register('dm', SerpDmModule);
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
}));
