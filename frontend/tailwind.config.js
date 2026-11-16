/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F17',
        surface: '#111827',
        surfaceMuted: '#1E293B',
        borderMuted: '#334155',
        brandPrimary: '#3B82F6',
        brandSecondary: '#6366F1',
        warningText: '#F59E0B',
        dangerText: '#EF4444',
        successText: '#10B981',
      },
    },
  },
  plugins: [],
};
