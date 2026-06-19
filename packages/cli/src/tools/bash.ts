import { exec } from 'child_process';
import { promisify } from 'util';
import os from 'os';
import type { ToolDefinition } from './types.js';

const execAsync = promisify(exec);

const BLOCKED_PATTERNS = [
  /\brm\s+-rf\s+\/(?!\w)/i,           // rm -rf / and variants
  /\brm\s+.*--no-preserve-root/i,       // rm --no-preserve-root
  /\bmkfs\b/i,                           // filesystem format
  /\bdd\s+if=.*of=\/dev/i,              // dd to raw device
  /:\(\)\s*\{\s*:.*[|&].*:.*[;&]/,      // fork bomb pattern
  /\bshutdown\b/i,
  /\breboot\b/i,
  /Remove-Item\s+.*-Recurse\b.*-Force\s+[CD]:\\/i,  // PowerShell rm -rf C:\
];

function isCommandBlocked(command: string): string | null {
  for (const pattern of BLOCKED_PATTERNS) {
    if (pattern.test(command)) {
      return `Blocked: command matches dangerous pattern (${pattern.source})`;
    }
  }
  return null;
}

export const bashTool: ToolDefinition = {
  spec: {
    name: 'bash',
    description: `Execute a shell command. On Windows this runs PowerShell; on Unix it runs bash.
Prefer this for: running scripts, installing packages, building projects, checking git status, etc.
Commands time out after 30 seconds by default.`,
    input_schema: {
      type: 'object',
      properties: {
        command: {
          type: 'string',
          description: 'The command to execute',
        },
        cwd: {
          type: 'string',
          description: 'Working directory (default: current directory)',
        },
        timeout_ms: {
          type: 'number',
          description: 'Timeout in milliseconds (default: 30000)',
        },
      },
      required: ['command'],
    },
  },
  execute: async (input) => {
    const command = input['command'] as string;
    const cwd = (input['cwd'] as string | undefined) ?? process.cwd();
    const timeoutMs = (input['timeout_ms'] as number | undefined) ?? 30000;

    const blockReason = isCommandBlocked(command);
    if (blockReason) {
      return blockReason;
    }

    const isWindows = os.platform() === 'win32';

    try {
      let stdout: string;
      let stderr: string;

      if (isWindows) {
        // Use -EncodedCommand with Base64 UTF-16LE to avoid all shell metacharacter injection
        const encoded = Buffer.from(command, 'utf16le').toString('base64');
        ({ stdout, stderr } = await execAsync(
          `powershell.exe -NonInteractive -NoProfile -EncodedCommand ${encoded}`,
          { cwd, timeout: timeoutMs, maxBuffer: 10 * 1024 * 1024 }
        ));
      } else {
        ({ stdout, stderr } = await execAsync(command, {
          cwd,
          timeout: timeoutMs,
          maxBuffer: 10 * 1024 * 1024,
          shell: '/bin/bash',
        }));
      }

      const parts: string[] = [];
      if (stdout.trim()) parts.push(stdout.trim());
      if (stderr.trim()) parts.push(`[stderr]\n${stderr.trim()}`);
      return parts.length > 0 ? parts.join('\n') : '(no output)';
    } catch (err) {
      const error = err as { message: string; stdout?: string; stderr?: string; killed?: boolean };
      if (error.killed) {
        return `Command timed out after ${timeoutMs}ms`;
      }
      const parts: string[] = [`Exit error: ${error.message}`];
      if (error.stdout?.trim()) parts.push(`stdout: ${error.stdout.trim()}`);
      if (error.stderr?.trim()) parts.push(`stderr: ${error.stderr.trim()}`);
      return parts.join('\n');
    }
  },
};
