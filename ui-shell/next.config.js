/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    // Allow external module bundles to be loaded
    async headers() {
        return [
            {
                source: '/api/:path*',
                headers: [
                    { key: 'Access-Control-Allow-Origin', value: '*' },
                ],
            },
        ];
    },
    // Proxy API requests to the backend (Python FastAPI on port 8000)
    async rewrites() {
        return [
            // Module bundles (loaded by script tags)
            {
                source: '/api/modules/:path*',
                destination: 'http://localhost:8000/api/modules/:path*',
            },
            // PM module API
            {
                source: '/api/pm/:path*',
                destination: 'http://localhost:8000/api/pm/:path*',
            },
            // UI config
            {
                source: '/api/ui-config/:path*',
                destination: 'http://localhost:8000/api/ui-config/:path*',
            },
        ];
    },
};

module.exports = nextConfig;

