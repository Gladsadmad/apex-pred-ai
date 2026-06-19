import Conf from 'conf';
import os from 'os';
import path from 'path';

export interface ApexConfig {
  apiKey?: string;
  model: string;
  maxTokens: number;
  debug: boolean;
  sessionHistoryDir: string;
  streamingEnabled: boolean;
  theme: 'dark' | 'light';
  swearingLevel: 'mild' | 'moderate' | 'full';
}

const DEFAULT_CONFIG: ApexConfig = {
  model: 'claude-sonnet-4-6',
  maxTokens: 8096,
  debug: false,
  sessionHistoryDir: path.join(os.homedir(), '.apex-pred', 'sessions'),
  streamingEnabled: true,
  theme: 'dark',
  swearingLevel: 'full',
};

const store = new Conf<ApexConfig>({
  projectName: 'apex-pred-ai',
  defaults: DEFAULT_CONFIG,
  schema: {
    apiKey: { type: 'string' },
    model: { type: 'string' },
    maxTokens: { type: 'number' },
    debug: { type: 'boolean' },
    sessionHistoryDir: { type: 'string' },
    streamingEnabled: { type: 'boolean' },
    theme: { type: 'string', enum: ['dark', 'light'] },
    swearingLevel: { type: 'string', enum: ['mild', 'moderate', 'full'] },
  },
});

export function getConfig(): ApexConfig {
  const config = store.store;

  const apiKey =
    process.env['ANTHROPIC_API_KEY'] ??
    process.env['APEX_API_KEY'] ??
    config.apiKey;

  const model = process.env['APEX_MODEL'] ?? config.model;

  // Guard against non-numeric APEX_MAX_TOKENS values
  let maxTokens = config.maxTokens;
  const maxTokensEnv = process.env['APEX_MAX_TOKENS'];
  if (maxTokensEnv) {
    const parsed = parseInt(maxTokensEnv, 10);
    if (!isNaN(parsed) && parsed > 0) maxTokens = parsed;
  }

  const debug = process.env['APEX_DEBUG'] === 'true' || config.debug;

  return { ...config, apiKey, model, maxTokens, debug };
}

export function setConfig(updates: Partial<ApexConfig>): void {
  for (const [key, value] of Object.entries(updates)) {
    if (value !== undefined) {
      store.set(key as keyof ApexConfig, value);
    }
  }
}

export function getConfigPath(): string {
  return store.path;
}

export { store };
