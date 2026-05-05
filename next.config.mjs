import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async redirects() {
    const categories = [
      'switches', 'panels', 'retrofit', 'sensors',
      'gateways', 'ir-blasters', 'led-controllers',
      'for-installers',
    ];
    const topLevel = [
      'getting-started', 'why-smartify', 'support', 'warranty',
    ];

    return [
      // Top-level pages: /getting-started → /docs/getting-started
      ...topLevel.map((slug) => ({
        source: `/${slug}`,
        destination: `/docs/${slug}`,
        permanent: true,
      })),
      // Category index: /gateways → /docs/gateways
      ...categories.map((slug) => ({
        source: `/${slug}`,
        destination: `/docs/${slug}`,
        permanent: true,
      })),
      // Product pages: /gateways/convergia → /docs/gateways/convergia
      ...categories.map((slug) => ({
        source: `/${slug}/:product`,
        destination: `/docs/${slug}/:product`,
        permanent: true,
      })),
    ];
  },
};

export default withMDX(config);
