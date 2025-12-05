/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
        "./components/**/*.{js,ts,jsx,tsx}",
        "./pages/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            // GeoNeuro Color Palette
            colors: {
                'geoneuro': {
                    'primary': 'rgb(99, 102, 241)',      // Indigo
                    'secondary': 'rgb(168, 85, 247)',   // Purple
                    'accent': 'rgb(16, 185, 129)',      // Emerald
                    'rural': 'rgb(16, 185, 129)',       // Emerald for rural
                    'urban': 'rgb(59, 130, 246)',       // Blue for urban
                },
            },
            // GeoNeuro Box Shadows (Glows)
            boxShadow: {
                'geoneuro-sm': '0 0 15px rgba(99, 102, 241, 0.2)',
                'geoneuro': '0 0 30px rgba(99, 102, 241, 0.35)',
                'geoneuro-lg': '0 0 50px rgba(99, 102, 241, 0.4)',
                'geoneuro-emerald': '0 0 30px rgba(16, 185, 129, 0.35)',
                'geoneuro-blue': '0 0 30px rgba(59, 130, 246, 0.35)',
                'geoneuro-purple': '0 0 30px rgba(168, 85, 247, 0.35)',
            },
            // GeoNeuro Gradients (via backgroundImage)
            backgroundImage: {
                'geoneuro-default': 'linear-gradient(to bottom, rgba(15, 23, 42, 0.95), rgba(88, 28, 135, 0.9), rgba(49, 46, 129, 0.85))',
                'geoneuro-rural': 'linear-gradient(to bottom, rgba(6, 78, 59, 0.95), rgba(20, 83, 45, 0.9), rgba(19, 78, 74, 0.85))',
                'geoneuro-urban': 'linear-gradient(to bottom, rgba(15, 23, 42, 0.95), rgba(30, 58, 138, 0.9), rgba(49, 46, 129, 0.85))',
                'geoneuro-glass': 'linear-gradient(to bottom, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02))',
            },
            // Animation timing functions
            transitionTimingFunction: {
                'geoneuro': 'cubic-bezier(0.25, 0.1, 0.25, 1)',
                'geoneuro-bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
            },
            // Animation durations
            transitionDuration: {
                '250': '250ms',
                '350': '350ms',
            },
            // Font families
            fontFamily: {
                'hindi': ['Noto Sans Devanagari', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
