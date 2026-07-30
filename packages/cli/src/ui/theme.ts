import chalk from 'chalk';

export const theme = {
  primary: chalk.hex('#FF4500'),
  secondary: chalk.hex('#FF8C00'),
  accent: chalk.hex('#FFD700'),
  success: chalk.hex('#00FF7F'),
  error: chalk.hex('#FF3333'),
  warning: chalk.hex('#FFA500'),
  muted: chalk.hex('#888888'),
  code: chalk.hex('#61AFEF'),
  string: chalk.hex('#98C379'),
  dim: chalk.dim,
  bold: chalk.bold,
  italic: chalk.italic,

  banner: (text: string): string => chalk.hex('#FF4500').bold(text),
  userPrompt: (text: string): string => chalk.hex('#FFD700').bold(`You: ${text}`),
  aiLabel: (): string => chalk.hex('#FF4500').bold('Apex-Pred: '),
  toolCall: (name: string): string => chalk.hex('#FF8C00')(`⚡ ${name}`),
  toolResult: (text: string): string => chalk.hex('#888888')(text),
  thinking: (): string => chalk.hex('#888888').italic('thinking...'),
  separator: (): string => chalk.hex('#333333')('─'.repeat(60)),

  boxConfig: {
    borderColor: 'red' as const,
    borderStyle: 'round' as const,
    padding: 1,
    margin: 0,
  },
};
