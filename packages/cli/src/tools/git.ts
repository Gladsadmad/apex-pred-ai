import { exec } from 'child_process';
import { promisify } from 'util';
import type { ToolDefinition } from './types.js';

const execAsync = promisify(exec);

async function git(command: string, cwd?: string): Promise<string> {
  const { stdout, stderr } = await execAsync(`git ${command}`, {
    cwd: cwd ?? process.cwd(),
    timeout: 30000,
  });
  return (stdout + stderr).trim();
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

    const blocked = ['push --force', 'reset --hard', 'clean -f', 'branch -D'];
    for (const b of blocked) {
      if (command.includes(b)) {
        return `Blocked: "${b}" requires explicit user confirmation. Tell the user and let them decide.`;
      }
    }

    try {
      return await git(command, cwd);
    } catch (err) {
      const error = err as { message: string };
      return `git error: ${error.message}`;
    }
  },
};
