import chalk from 'chalk';
import { theme } from './theme.js';

// Lightweight terminal markdown formatter using chalk directly.
// Avoids the marked + marked-terminal incompatibility (marked v12 rejects
// marked-terminal's minified renderer property names at runtime).
export function renderMarkdown(text: string): string {
  return (
    text
      // Fenced code blocks (```lang\n...\n```)
      .replace(/```(?:\w+)?\n([\s\S]*?)```/g, (_, code: string) =>
        chalk.hex('#61AFEF')(code.trimEnd()) + '\n'
      )
      // Inline code
      .replace(/`([^`\n]+)`/g, (_, code: string) => chalk.hex('#61AFEF')(code))
      // H1
      .replace(/^# (.+)$/gm, (_, t: string) => chalk.hex('#FF4500').bold(t))
      // H2
      .replace(/^## (.+)$/gm, (_, t: string) => chalk.hex('#FF8C00').bold(t))
      // H3+
      .replace(/^#{3,} (.+)$/gm, (_, t: string) => chalk.bold(t))
      // Bold
      .replace(/\*\*([^*\n]+)\*\*/g, (_, t: string) => chalk.bold(t))
      // Italic
      .replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g, (_, t: string) => chalk.italic(t))
      // Blockquotes
      .replace(/^> (.+)$/gm, (_, t: string) => chalk.hex('#888888').italic(`  ${t}`))
      // Unordered list items
      .replace(/^[ \t]*[-*+] (.+)$/gm, (_, t: string) => chalk.hex('#FFD700')(`  • ${t}`))
      // Horizontal rules
      .replace(/^[-*_]{3,}$/gm, () => theme.separator())
  );
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
