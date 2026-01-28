/**
 * SERP HMR Plugin for Vite
 *
 * This plugin enables Hot Module Replacement for SERP modules.
 * It broadcasts custom events via Vite's WebSocket when files change,
 * allowing the UI Shell to reload module bundles without page refresh.
 */
import type { Plugin, ViteDevServer } from 'vite';

export interface SerpHmrPluginOptions {
    /** Module ID (e.g., 'pm', 'crm') */
    moduleId: string;
    /** Port for the dev server (default: 5173) */
    port?: number;
}

/**
 * Creates a Vite plugin that broadcasts module update events for HMR
 *
 * @example
 * ```typescript
 * // vite.config.ts
 * import { serpHmrPlugin } from './hmr-plugin';
 *
 * export default defineConfig({
 *     plugins: [react(), serpHmrPlugin({ moduleId: 'pm', port: 5173 })],
 * });
 * ```
 */
export function serpHmrPlugin(options: SerpHmrPluginOptions): Plugin {
    const { moduleId, port = 5173 } = options;
    let server: ViteDevServer | null = null;

    return {
        name: 'serp-hmr',

        configureServer(viteServer) {
            server = viteServer;

            // Log when clients connect
            server.ws.on('connection', (socket) => {
                console.log(`🔥 [HMR] Client connected for module: ${moduleId}`);

                socket.on('close', () => {
                    console.log(`🔥 [HMR] Client disconnected from module: ${moduleId}`);
                });
            });

            // Add custom endpoint for module info
            server.middlewares.use('/serp-hmr-info', (_req, res) => {
                res.setHeader('Content-Type', 'application/json');
                res.setHeader('Access-Control-Allow-Origin', '*');
                res.end(
                    JSON.stringify({
                        moduleId,
                        port,
                        timestamp: Date.now(),
                    })
                );
            });

            console.log(`🔥 [HMR] SERP HMR plugin initialized for module: ${moduleId} on port ${port}`);
        },

        handleHotUpdate({ file, server: viteServer }) {
            // Only broadcast for relevant file changes
            const relevantExtensions = ['.tsx', '.ts', '.jsx', '.js', '.css'];
            const isRelevant = relevantExtensions.some((ext) => file.endsWith(ext));

            if (isRelevant) {
                console.log(`🔥 [HMR] File changed: ${file}`);

                // Broadcast custom event to all connected clients
                viteServer.ws.send({
                    type: 'custom',
                    event: 'serp:module-update',
                    data: {
                        moduleId,
                        file,
                        timestamp: Date.now(),
                    },
                });

                console.log(`🔥 [HMR] Broadcasted update event for module: ${moduleId}`);
            }
        },
    };
}

export default serpHmrPlugin;
