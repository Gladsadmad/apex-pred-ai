import { marked } from 'marked';
import TerminalRenderer from 'marked-terminal';
import chalk from 'chalk';
import { theme } from './theme.js';

marked.setOptions({
  renderer: new TerminalRenderer({
    code: chalk.hex('#61AFEF'),
    codespan: chalk.hex('#61AFEF'),
    firstHeading: chalk.hex('#FF4500').bold,
    heading: chalk.hex('#FF8C00').bold,
    strong: chalk.bold,
    em: chalk.italic,
    blockquote: chalk.hex('#888888').italic,
    hr: () => theme.separator() + '\n',
    listitem: chalk.hex('#FFD700'),
  }) as never,
});

export function renderMarkdown(text: string): string {
  return marked(text) as string;
}

export function renderToolCall(name: string, input: Record<string, unknown>): string {
  const inputStr = JSON.stringify(input, null, 2)
    .split('\n')
    .map(line => `  ${line}`)
    .join('\n');
  return `${theme.toolCall(name)}\n${theme.muted(inputStr)}`;
}

export function renderError(message: string): string {
  return theme.error(`✗ Error: ${message}`);
}

export function renderSuccess(message: string): string {
  return theme.success(`✓ ${message}`);
}

export function renderInfo(message: string): string {
  return theme.muted(`ℹ ${message}`);
}

export function renderUserInput(input: string): string {
  return theme.userPrompt(input);
}
