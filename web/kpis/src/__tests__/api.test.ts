import request from 'supertest';
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';

// build a minimal app using the same middlewares to test routes
function buildApp() {
  const app = express();
  app.use(helmet());
  app.use(cors({ origin: true }));
  app.use(morgan('tiny'));
  app.get('/healthz', (_req, res) => res.json({ status: 'ok' }));
  return app;
}

describe('API', () => {
  it('healthz returns ok', async () => {
    const app = buildApp();
    const res = await request(app).get('/healthz');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });
});


