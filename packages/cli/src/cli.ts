import readline from 'readline';
import process from 'process';
import boxen from 'boxen';
import chalk from 'chalk';
import { theme } from './ui/theme.js';
import { APEX_PRED_BANNER, WELCOME_MESSAGE } from './personality.js';
import { ApexPredAgent } from './agent.js';
import type { ApexConfig } from './config.js';

const SLASH_COMMANDS: Record<string, string> = {
  '/help': 'Show available commands',
  '/tools': 'List available tools',
  '/config': 'Show current config',
  '/clear': 'Clear conversation history',
  '/session': 'Show session info',
  '/exit': 'Exit Apex-Pred AI',
  '/quit': 'Exit Apex-Pred AI',
};

function printHelp(): void {
  console.log('\n' + theme.secondary.bold('Slash Commands:'));
  for (const [cmd, desc] of Object.entries(SLASH_COMMANDS)) {
    console.log(`  ${theme.primary(cmd.padEnd(12))} ${theme.muted(desc)}`);
  }
  console.log();
}

function printBanner(): void {
  console.log(theme.banner(APEX_PRED_BANNER));
  console.log(
    boxen(theme.muted(WELCOME_MESSAGE), {
      borderColor: 'red',
      borderStyle: 'round',
      padding: 1,
    })
  );
}

export async function startInteractive(config: ApexConfig): Promise<void> {
  printBanner();

  const agent = new ApexPredAgent(config);
  const useStreaming = config.streamingEnabled;

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: true,
    prompt: chalk.hex('#FF4500').bold('\nYou → '),
  });

  rl.prompt();

  rl.on('line', async (line) => {
    const input = line.trim();

    if (!input) {
      rl.prompt();
      return;
    }

    if (input.startsWith('/')) {
      const cmd = input.split(' ')[0]?.toLowerCase();

      switch (cmd) {
        case '/help':
          printHelp();
          break;

        case '/tools':
          console.log('\n' + theme.secondary.bold('Available Tools:'));
          for (const tool of agent.listTools()) {
            console.log(`  ${theme.primary('⚡')} ${tool}`);
          }
          console.log();
          break;

        case '/config':
          console.log('\n' + theme.secondary.bold('Current Config:'));
          console.log(`  Model:      ${theme.accent(config.model)}`);
          console.log(`  Max Tokens: ${theme.accent(String(config.maxTokens))}`);
          console.log(`  Streaming:  ${theme.accent(String(config.streamingEnabled))}`);
          console.log(`  Debug:      ${theme.accent(String(config.debug))}`);
          console.log(`  API Key:    ${config.apiKey ? theme.success('✓ set') : theme.error('✗ missing')}`);
          console.log();
          break;

        case '/clear':
          agent.clearSession();
          console.clear();
          printBanner();
          console.log(theme.success('Conversation cleared. Fresh start, baby.\n'));
          break;

        case '/session': {
          const info = agent.getSessionInfo();
          console.log('\n' + theme.secondary.bold('Session Info:'));
          console.log(`  ID:       ${theme.muted(info.id)}`);
          console.log(`  Messages: ${theme.accent(String(info.messageCount))}`);
          console.log(`  Tokens:   ${theme.accent(String(info.tokensUsed))}`);
          console.log();
          break;
        }

        case '/exit':
        case '/quit':
          console.log(theme.muted('\nApex-Pred out. Stay sharp.\n'));
          process.exit(0);
          break;

        default:
          console.log(theme.error(`\nUnknown command: ${cmd}. Type /help for a list.\n`));
      }

      rl.prompt();
      return;
    }

    rl.pause();

    try {
      if (useStreaming) {
        await agent.streamingChat(input);
      } else {
        await agent.chat(input);
      }
    } catch (err) {
      const error = err as { message: string };
      console.error(theme.error(`\nUnexpected error: ${error.message}`));
    } finally {
      rl.resume();
      rl.prompt();
    }
  });

  rl.on('close', () => {
    console.log(theme.muted('\nApex-Pred out. Stay sharp.\n'));
    process.exit(0);
  });

  process.on('SIGINT', () => {
    console.log(theme.muted('\n\nCaught interrupt. Apex-Pred out.\n'));
    process.exit(0);
  });
}

export async function runOneShot(message: string, config: ApexConfig): Promise<void> {
  const agent = new ApexPredAgent(config);
  if (config.streamingEnabled) {
    await agent.streamingChat(message);
  } else {
    await agent.chat(message);
  }
}
