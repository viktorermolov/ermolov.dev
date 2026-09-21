import { defineConfig } from 'vitest/config';
import { cloudflareTest, readD1Migrations } from '@cloudflare/vitest-pool-workers';

export default defineConfig(async () => ({
  plugins: [cloudflareTest({
    wrangler: { configPath: './wrangler.jsonc' },
    miniflare: {
      // The test pool currently bundles a runtime from August; production stays current.
      compatibilityDate: '2026-08-15',
      bindings: {
        TURNSTILE_SECRET_KEY: 'test-secret-not-a-production-key',
        RELAY_TOKEN: 'local-test-relay-token-longer-than-32-characters',
        TEST_MIGRATIONS: await readD1Migrations('./migrations'),
      },
    },
  })],
  test: { include: ['test/**/*.test.ts'], fileParallelism: false },
}));
