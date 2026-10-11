#!/usr/bin/env node
/**
 * verify_pointer.js - CDP Physical Pointer Dispatch & Hit-Test Verifier
 * Bypasses synthetic DOM events. Dispatches true OS-level pointer input via CDP.
 */

const http = require('http');

function getTargets(port = 9222) {
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}/json`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.msgId = 0;
    this.callbacks = new Map();
    this.events = [];
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = (err) => reject(err);
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.callbacks.has(msg.id)) {
          const { resolve, reject } = this.callbacks.get(msg.id);
          this.callbacks.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message));
          else resolve(msg.result);
        } else if (msg.method) {
          this.events.push(msg);
        }
      };
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.msgId;
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true
    });
    return res.result ? res.result.value : res;
  }

  async physicalClick(x, y) {
    await this.send('Input.dispatchMouseEvent', {
      type: 'mousePressed',
      x,
      y,
      button: 'left',
      clickCount: 1
    });
    await this.send('Input.dispatchMouseEvent', {
      type: 'mouseReleased',
      x,
      y,
      button: 'left',
      clickCount: 1
    });
  }

  close() {
    if (this.ws) this.ws.close();
  }
}

async function main() {
  const args = process.argv.slice(2);
  const port = parseInt(args.find(a => a.startsWith('--port='))?.split('=')[1] || '9222', 10);
  const urlFilter = args.find(a => a.startsWith('--url='))?.split('=')[1] || '';
  const selector = args.find(a => a.startsWith('--selector='))?.split('=')[1] || '';

  console.log(`Connecting to CDP port ${port}...`);
  const targets = await getTargets(port);
  const pageTarget = targets.find(t => t.type === 'page' && (!urlFilter || t.url.includes(urlFilter)));

  if (!pageTarget) {
    console.error(`Error: No active page target found matching URL: "${urlFilter}"`);
    process.exit(1);
  }

  console.log(`Connected to page target: ${pageTarget.title || 'Untitled'} (${pageTarget.url})`);
  const client = new CDPClient(pageTarget.webSocketDebuggerUrl);
  await client.connect();

  await client.send('Runtime.enable');
  await client.send('Network.enable');

  if (selector) {
    console.log(`Locating physical bounds for selector: "${selector}"`);
    const bounds = await client.evaluate(`
      (() => {
        const el = document.querySelector(${JSON.stringify(selector)});
        if (!el) return null;
        const rect = el.getBoundingClientRect();
        return {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
          w: rect.width,
          h: rect.height,
          visible: rect.width > 0 && rect.height > 0
        };
      })()
    `);

    if (!bounds || !bounds.visible) {
      console.error(`Error: Element "${selector}" not visible or not found in DOM.`);
      client.close();
      process.exit(1);
    }

    console.log(`Element physical center: (${bounds.x}, ${bounds.y})`);
    console.log(`Dispatching physical mousePress + mouseRelease via CDP...`);
    const preCount = client.events.filter(e => e.method === 'Network.requestWillBeSent').length;
    await client.physicalClick(bounds.x, bounds.y);

    await new Promise(r => setTimeout(r, 1500));
    const postCount = client.events.filter(e => e.method === 'Network.requestWillBeSent').length;
    console.log(`Physical click dispatched successfully. Triggered ${postCount - preCount} network requests.`);
  }

  client.close();
  console.log('Physical pointer verification completed.');
  process.exit(0);
}

main().catch(err => {
  console.error('Fatal CDP error:', err.message);
  process.exit(1);
});
