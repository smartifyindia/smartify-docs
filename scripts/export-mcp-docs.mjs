import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, relative, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const hash = text => createHash('sha256').update(text).digest('hex');
const walk = dir => readdirSync(dir, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? walk(resolve(dir, entry.name)) : entry.name.endsWith('.mdx') ? [resolve(dir, entry.name)] : []);
const clean = text => text.replace(/!\[[^\]]*\]\([^)]*\)/g, '').replace(/<[^>]+>/g, '').replace(/\{\/\*[\s\S]*?\*\/\}/g, '').trim();
const mappingsPath = resolve(root, 'lib/mcp-docs/product-identities.json');
const identities = JSON.parse(readFileSync(mappingsPath, 'utf8'));
const docs = walk(resolve(root, 'content/docs/products')).sort().map(file => {
  const source = readFileSync(file, 'utf8');
  const id = relative(resolve(root, 'content/docs'), file).replace(/\.mdx$/, '');
  const titleField = source.match(/^title:\s*(.+)$/m)?.[1];
  const title = titleField?.startsWith('"') ? JSON.parse(titleField) : titleField || id;
  const body = source.replace(/^---\n[\s\S]*?\n---\n/, '');
  const sections = [];
  let heading = 'Overview'; let lines = [];
  const flush = () => { const text = clean(lines.join('\n')); if (text) sections.push({ heading, text, hash: hash(text) }); };
  for (const line of body.split('\n')) {
    const match = line.match(/^#{2,3}\s+(.+)$/);
    if (match) { flush(); heading = match[1]; lines = []; } else lines.push(line);
  }
  flush();
  // Product aliases are a reviewed snapshot, never resolved from caller URLs or fuzzy names.
  return { id, title, skus: source.match(/^sku:\s*"([A-Za-z0-9_-]+)"$/m) ? [source.match(/^sku:\s*"([A-Za-z0-9_-]+)"$/m)[1]] : (identities[id]?.title === title ? identities[id].skus : []), url: 'https://docs.smartify.in/docs/' + id, hash: hash(source), sourcePath: relative(root, file), sections };
});
writeFileSync(resolve(root, 'lib/mcp-docs/index.json'), JSON.stringify(docs, null, 2) + '\n');
console.log(`Exported ${docs.length} public product documents.`);
