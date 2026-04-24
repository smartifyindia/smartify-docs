import type { Config } from 'tailwindcss';
import { createPreset } from 'fumadocs-ui/tailwind-plugin';

const config: Config = {
  content: [
    './node_modules/fumadocs-ui/dist/**/*.js',
    './app/**/*.{ts,tsx}',
    './content/**/*.{md,mdx}',
    './mdx-components.tsx',
  ],
  presets: [createPreset()],
  theme: {
    extend: {
      colors: {
        // Smartify design system
        primary: {
          DEFAULT: '#0FABBB',
          50: 'rgba(15, 171, 187, 0.04)',
          100: 'rgba(15, 171, 187, 0.08)',
          200: 'rgba(15, 171, 187, 0.16)',
          300: 'rgba(15, 171, 187, 0.24)',
          400: 'rgba(15, 171, 187, 0.50)',
          500: '#0FABBB',
        },
        dark: {
          DEFAULT: '#0f172a',
          secondary: '#475569',
          tertiary: '#94a3b8',
          extreme: '#020617',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};

export default config;
