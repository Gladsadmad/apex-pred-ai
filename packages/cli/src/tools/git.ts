import { execFile } from 'child_process';
import { promisify } from 'util';
import type { ToolDefinition } from './types.js';

const execFileAsync = promisify(execFile);

// Regex-based blocklist — resistant to whitespace variations and case differences
const BLOCKED_GIT = [
  /\bpush\s+.*--force\b/i,
  /\bpush\s+-f\b/i,
  /\breset\s+--hard\b/i,
  /\bclean\s+-[a-z]*f/i,
  /\bbranch\s+-D\b/i,
];

function isGitCommandBlocked(command: string): string | null {
  for (const pattern of BLOCKED_GIT) {
    if (pattern.test(command)) {
      return `Blocked: "${command}" matches ${pattern.source}. Tell the user and let them decide.`;
    }
  }
  return null;
}

async function runGit(command: string, cwd: string): Promise<string> {
  // Split into args array so execFile never passes through a shell — no injection possible
  const args = command.trim().split(/\s+/).filter(Boolean);
  const { stdout, stderr } = await execFileAsync('git', args, {
    cwd,
    timeout: 30000,
  });
  const parts: string[] = [];
  if (stdout.trim()) parts.push(stdout.trim());
  if (stderr.trim()) parts.push(stderr.trim());
  return parts.join('\n') || '(no output)';
}

export const gitTool: ToolDefinition = {
  spec: {
    name: 'git',
    description: `Execute git commands. Use this for: checking status, viewing diffs, staging files, committing, branching, logging, etc.
Provide the git subcommand and args (without the "git" prefix).`,
    input_schema: {
      type: 'object',
      properties: {
        command: {
          type: 'string',
          description: 'Git command and args (e.g. "status", "log --oneline -10", "diff HEAD")',
        },
        cwd: {
          type: 'string',
          description: 'Working directory (default: current directory)',
        },
      },
      required: ['command'],
    },
  },
  execute: async (input) => {
    const command = input['command'] as string;
    const cwd = (input['cwd'] as string | undefined) ?? process.cwd();

    const blockReason = isGitCommandBlocked(command);
    if (blockReason) return blockReason;

    try {
      return await runGit(command, cwd);
    } catch (err) {
      const error = err as { message: string };
      return `git error: ${error.message}`;
    }
  },
};
