/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/**/*.{js,ts,jsx,tsx,mdx}',
        // Plugin modules - shell doesn't know specific modules, just the pattern
        '../modules/*/serp_*/ui/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {},
    },
    plugins: [require('tailwindcss-animate')],
};
