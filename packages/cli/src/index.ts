import { program } from 'commander';
import chalk from 'chalk';
import { getConfig, setConfig, getConfigPath } from './config.js';
import { startInteractive, runOneShot } from './cli.js';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const pkgPath = join(__dirname, '..', 'package.json');
let version = '1.0.0';
try {
  const pkg = JSON.parse(readFileSync(pkgPath, 'utf-8')) as { version: string };
  version = pkg.version;
} catch {
  // ignore
}

program
  .name('apex')
  .description('Apex-Pred AI — the apex predator of AI assistants')
  .version(version, '-v, --version', 'Show version')
  .argument('[message...]', 'One-shot message to send')
  .option('-k, --key <key>', 'Anthropic API key (overrides env/config)')
  .option('-m, --model <model>', 'Model to use (default: claude-sonnet-4-6)')
  .option('-t, --max-tokens <tokens>', 'Max tokens per response', parseInt)
  .option('--no-stream', 'Disable streaming output')
  .option('--debug', 'Enable debug logging')
  .action(async (messageParts: string[], opts) => {
    const config = getConfig();

    if (opts['key']) config.apiKey = opts['key'] as string;
    if (opts['model']) config.model = opts['model'] as string;
    if (opts['maxTokens']) config.maxTokens = opts['maxTokens'] as number;
    if (opts['stream'] === false) config.streamingEnabled = false;
    if (opts['debug']) config.debug = true;

    if (messageParts.length > 0) {
      await runOneShot(messageParts.join(' '), config);
    } else {
      await startInteractive(config);
    }
  });

program
  .command('config')
  .description('View or update Apex-Pred AI configuration')
  .option('-k, --key <key>', 'Set Anthropic API key')
  .option('-m, --model <model>', 'Set default model')
  .option('-t, --max-tokens <tokens>', 'Set max tokens per response', parseInt)
  .option('--no-stream', 'Disable streaming by default')
  .option('--stream', 'Enable streaming by default')
  .option('--debug', 'Enable debug mode')
  .option('--no-debug', 'Disable debug mode')
  .option('--show', 'Show current config and exit')
  .action((opts) => {
    const config = getConfig();

    if (opts['show'] || Object.keys(opts).every(k => !opts[k])) {
      console.log(chalk.hex('#FF4500').bold('\nApex-Pred AI Configuration'));
      console.log(chalk.hex('#888888')(`Config file: ${getConfigPath()}\n`));
      console.log(`  API Key:    ${config.apiKey ? chalk.green('✓ set') : chalk.red('✗ not set')}`);
      console.log(`  Model:      ${chalk.yellow(config.model)}`);
      console.log(`  Max Tokens: ${chalk.yellow(String(config.maxTokens))}`);
      console.log(`  Streaming:  ${chalk.yellow(String(config.streamingEnabled))}`);
      console.log(`  Debug:      ${chalk.yellow(String(config.debug))}`);
      console.log();
      return;
    }

    const updates: Record<string, unknown> = {};
    if (opts['key']) updates['apiKey'] = opts['key'];
    if (opts['model']) updates['model'] = opts['model'];
    if (opts['maxTokens']) updates['maxTokens'] = opts['maxTokens'];
    if ('stream' in opts) updates['streamingEnabled'] = opts['stream'];
    if ('debug' in opts) updates['debug'] = opts['debug'];

    setConfig(updates);
    console.log(chalk.green('\n✓ Configuration updated.\n'));
  });

program
  .command('version')
  .description('Show version information')
  .action(() => {
    console.log(`Apex-Pred AI v${version}`);
    console.log('The apex predator of AI assistants.');
  });

program.parseAsync(process.argv).catch((err: Error) => {
  console.error(chalk.red(`\nFatal error: ${err.message}\n`));
  process.exit(1);
});
