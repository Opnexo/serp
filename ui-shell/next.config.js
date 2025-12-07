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
};

module.exports = nextConfig;
