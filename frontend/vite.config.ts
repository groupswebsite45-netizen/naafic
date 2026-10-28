import { defineConfig, Plugin } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// Catch unhandled socket resets and client aborts at the Node process level (Node 24 on Windows)
const IGNORED_SOCKET_ERRORS = new Set(['ECONNRESET', 'EPIPE', 'ECONNABORTED', 'ETIMEDOUT', 'HPE_INVALID_EOF_STATE']);

process.on('uncaughtException', (err: any) => {
  if (err && (IGNORED_SOCKET_ERRORS.has(err.code) || err.message?.includes('ECONNRESET') || err.message?.includes('EPIPE'))) {
    // Normal browser navigation/refresh socket teardown - safely ignore to prevent dev server crash
    return;
  }
  console.error('[Vite Process uncaughtException]', err);
});

process.on('unhandledRejection', (reason: any) => {
  if (reason && (IGNORED_SOCKET_ERRORS.has(reason.code) || reason.message?.includes('ECONNRESET') || reason.message?.includes('EPIPE'))) {
    return;
  }
  console.error('[Vite Process unhandledRejection]', reason);
});

// Vite plugin providing comprehensive connection error immunity & socket resilience
function devServerResiliencePlugin(): Plugin {
  return {
    name: 'dev-server-resilience',
    configureServer(server) {
      // 1. Intercept client socket errors on the underlying HTTP server
      server.httpServer?.on('connection', (socket) => {
        socket.on('error', (err: any) => {
          if (IGNORED_SOCKET_ERRORS.has(err?.code)) {
            socket.destroy();
          }
        });
      });

      // 2. Handle HTTP protocol-level client parse errors (e.g. abrupt browser reload during request)
      server.httpServer?.on('clientError', (err: any, socket) => {
        if (IGNORED_SOCKET_ERRORS.has(err?.code) || socket.destroyed) {
          socket.destroy();
          return;
        }
        socket.end('HTTP/1.1 400 Bad Request\r\n\r\n');
      });

      // 3. WebSocket HMR server resilience
      if (server.ws) {
        server.ws.on('error', (err: any) => {
          if (IGNORED_SOCKET_ERRORS.has(err?.code)) {
            return;
          }
          console.warn('[Vite HMR WebSocket]', err?.message || err);
        });
      }
    },
  };
}

export default defineConfig({
  plugins: [vue(), devServerResiliencePlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    watch: {
      ignored: [
        '**/dist/**',
        '**/.git/**',
        '**/node_modules/**',
        '**/backend/**',
        '**/*~',
        '**/*.tmp',
        '**/.#*',
      ],
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: false,
        configure: (proxy) => {
          proxy.on('error', (err: any, _req, res: any) => {
            // If backend is unavailable or restarting, respond gracefully instead of terminating Vite
            if (res && 'writeHead' in res && !res.headersSent && !res.writableEnded) {
              res.writeHead(503, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                success: false,
                message: 'Backend server is temporarily unavailable or restarting',
                code: err.code || 'PROXY_ERROR',
              }));
            }
          });
        },
      },
    },
  },
});
