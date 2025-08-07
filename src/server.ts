import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { serve } from '@hono/node-server'
import { serveStatic } from '@hono/node-server/serve-static'
import { readFile } from 'node:fs/promises'


const isProd = process.env['NODE_ENV'] === 'production'

let html = await readFile(isProd ? 'dist/index.html' : 'index.html', 'utf8')

console.log(`Running on: ${isProd ? 'production' : 'development'}`)

if (!isProd) {
  html = html.replace('<head>', `
  <script type="module" src="/@vite/client"></script>
  `)
}

const app = new Hono()
  .use('/*', serveStatic({ root: isProd ? 'dist/' : './' }))
  .use('/assets/*', serveStatic({ root: isProd ? 'dist/assets' : './' }))
  .use('/dist/*', serveStatic({ root: 'dist/' }));

  // .get('/api', c => c.json( { count: parseInt(c.req.query('count')!) * 2} ))
  // .get('/*', c => c.html(html))


// Middleware
app.use('*', logger());
app.use('*', cors());

// Health check
app.get('/health', (c) => {
  return c.json({ status: 'ok', timestamp: new Date().toISOString() });
})

app.get('/*', c => c.html(html));

// --- General Middleware ---
app.use("*", async (c, next) => {
  c.res.headers.set("X-Powered-By", "Hono")
  await next()
})

export default app


if (isProd) {
  serve({ ...app, port: process.env['PORT']? parseInt(process.env['PORT'], 10) : 3000 }, info => {
    console.log(`Listening on http://localhost:${info.port}\nUse Ctrl+C to stop the server`)
  })
}
