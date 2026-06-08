import { createReadStream, existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { defineConfig } from 'vite';

function isDeliverySuccess(data) {
  if (!data || typeof data !== 'object') return false;
  const flag = data.success;
  return flag === true || flag === 'true';
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

function contactApiPlugin() {
  const attach = (middlewares, root) => {
    const handler = async (req, res, next) => {
      const pathname = (req.url ?? '').split('?')[0];
      if (pathname !== '/api/contact' || req.method !== 'POST') {
        return next();
      }

      try {
        const raw = await readBody(req);
        const payload = JSON.parse(raw || '{}');
        const name = String(payload.name || '').trim();
        const email = String(payload.email || '').trim();
        const message = String(payload.message || '').trim();

        if (!name || !email || !message) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ success: false, message: 'Missing required fields.' }));
          return;
        }

        const profilePath = join(root, '..', 'scripts', 'resume-profile.json');
        const profile = JSON.parse(readFileSync(profilePath, 'utf-8'));
        const recipient = profile.profile.email;
        const web3Key = profile.contactForm?.web3formsAccessKey || '';
        const formsubmitId = profile.contactForm?.formsubmitFormId || '';
        const formsubmitEndpoint = formsubmitId || recipient;
        const subject = `Portfolio message from ${name}`;
        let errorMsg = 'Unable to send message. Please try again.';

        if (web3Key) {
          const web3Res = await fetch('https://api.web3forms.com/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            body: JSON.stringify({
              access_key: web3Key,
              name,
              email,
              message,
              subject,
            }),
          });
          const web3Data = await web3Res.json().catch(() => ({}));
          if (web3Res.ok && isDeliverySuccess(web3Data)) {
            res.statusCode = 200;
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({ success: true }));
            return;
          }
          errorMsg = web3Data.message || errorMsg;
        }

        const formBody = new FormData();
        formBody.append('name', name);
        formBody.append('email', email);
        formBody.append('message', message);
        formBody.append('_subject', subject);
        formBody.append('_captcha', 'false');
        formBody.append('_template', 'table');

        const formRes = await fetch(
          `https://formsubmit.co/ajax/${encodeURIComponent(formsubmitEndpoint)}`,
          {
            method: 'POST',
            headers: { Accept: 'application/json' },
            body: formBody,
          }
        );
        const formData = await formRes.json().catch(() => ({}));
        if (formRes.ok && isDeliverySuccess(formData)) {
          res.statusCode = 200;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ success: true }));
          return;
        }

        const deliveryMessage = formData.message || formData.error || errorMsg;
        res.statusCode = 502;
        res.setHeader('Content-Type', 'application/json');
        res.end(
          JSON.stringify({
            success: false,
            message: deliveryMessage,
          })
        );
      } catch {
        res.statusCode = 500;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ success: false, message: 'Server error. Please try again.' }));
      }
    };

    middlewares.stack.unshift({ route: '', handle: handler });
  };

  return {
    name: 'contact-api',
    configureServer(server) {
      attach(server.middlewares, server.config.root);
    },
    configurePreviewServer(server) {
      attach(server.middlewares, server.config.root);
    },
  };
}

/** Pre-built Astro bundle — serve raw; Vite transform bloats it ~5x and breaks load. */
function serveAstroBundleRaw() {
  return {
    name: 'serve-astro-bundle-raw',
    configureServer(server) {
      const handler = (req, res, next) => {
        const pathname = (req.url ?? '').split('?')[0];
        if (!pathname.startsWith('/_astro/') || !pathname.endsWith('.js')) {
          return next();
        }

        const filePath = join(server.config.root, pathname.slice(1));
        if (!existsSync(filePath)) {
          return next();
        }

        res.statusCode = 200;
        res.setHeader('Content-Type', 'text/javascript');
        createReadStream(filePath).pipe(res);
      };

      server.middlewares.stack.unshift({ route: '', handle: handler });
    },
  };
}

export default defineConfig({
  // Avoid SPA fallback: missing /assets/* must 404, not return index.html (breaks loaders).
  appType: 'mpa',
  root: 'public',
  publicDir: false,
  server: {
    host: '127.0.0.1',
    port: 5136,
    strictPort: true,
    open: 'http://127.0.0.1:5136/',
    headers: {
      'Cache-Control': 'no-store',
    },
  },
  preview: {
    host: '127.0.0.1',
    port: 5136,
    strictPort: true,
  },
  assetsInclude: ['**/*.buf'],
  plugins: [serveAstroBundleRaw(), contactApiPlugin()],
});
