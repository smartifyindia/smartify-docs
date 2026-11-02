import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createServer } from 'node:net';

// Exercise the production HTTP routes, not implementation details.
const socket = createServer();
socket.listen(0, '127.0.0.1');
await once(socket, 'listening');
const port = socket.address().port;
await new Promise((resolve) => socket.close(resolve));
const server = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'start', '-p', String(port)], { stdio: 'inherit' });
const base = `http://127.0.0.1:${port}`;
async function get(path) {
  const response = await fetch(base + path, { signal: AbortSignal.timeout(30_000) });
  assert.equal(response.status, 200, path);
  return response;
}
try {
  let ready = false;
  for (let attempt = 0; attempt < 120; attempt++) {
    try { await fetch(base, { signal: AbortSignal.timeout(2000) }); ready = true; break; } catch {}
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  assert.ok(ready, 'Production server started');
  const robots = await (await get('/robots.txt')).text();
  assert.match(robots, /User-agent: \*/);
  assert.match(robots, /Content-Signal: search=yes, ai-input=yes, ai-train=no/);
  assert.match(robots, /Sitemap: https:\/\/docs.smartify.in\/sitemap.xml/);
  const sitemap = await (await get('/sitemap.xml')).text();
  const urls = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) => match[1]);
  assert.ok(urls.length > 80);
  assert.equal(new Set(urls).size, urls.length);
  assert.ok(urls.every((url) => url.startsWith('https://docs.smartify.in/docs/')));
  const home = await get('/');
  assert.match(home.headers.get('link'), /rel="sitemap"/);
  assert.match(home.headers.get('link'), /rel="api-catalog"/);
  const index = await (await get('/llms.txt')).text();
  assert.match(index, /^# Smartify Docs/);
  assert.match(index, /llms-full.txt/);
  assert.match(index, /https:\/\/docs.smartify.in\/docs\/products/);
  const full = await get('/llms-full.txt');
  assert.match(full.headers.get('content-type'), /text\/plain/);
  assert.match(await full.text(), /Zigbee/);
  const catalog = await get('/.well-known/api-catalog');
  assert.match(catalog.headers.get('content-type'), /application\/linkset\+json/);
  const entries = (await catalog.json()).linkset;
  assert.equal(entries[0].anchor, 'https://docs.smartify.in/api/search');
  const spec = await (await get('/openapi.json')).json();
  assert.ok(spec.paths['/api/search'].get);
  const results = await (await get('/api/search?query=zigbee')).json();
  assert.ok(results.length > 0);
  console.log('Agent discovery HTTP tests passed');
} finally {
  server.kill('SIGTERM');
  await once(server, 'exit');
}
