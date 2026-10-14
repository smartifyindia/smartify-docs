import { copyFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const apiRoot = process.env.SMARTIFY_API_DIR || resolve(root, '../smartify-pro/smartify-pro-backend');
await mkdir(resolve(root, 'public/openapi'), { recursive: true });
await copyFile(resolve(apiRoot, 'openapi/partner-catalog.openapi.json'), resolve(root, 'public/openapi/partner-catalog.openapi.json'));
await copyFile(resolve(root, 'guides/partner-catalog-api.mdx'), resolve(root, 'content/docs/smartify-pro/partner-catalog-api.mdx'));
await copyFile(resolve(apiRoot, 'openapi/partner-assistance.openapi.json'), resolve(root, 'public/openapi/partner-assistance.openapi.json'));
await copyFile(resolve(root, 'guides/partner-assistance.mdx'), resolve(root, 'content/docs/smartify-pro/partner-assistance.mdx'));
console.log('Partner catalog guide and OpenAPI reference synchronized.');
