import fs from 'fs/promises';
import path from 'path';
import { glob } from 'glob';
import type { ToolDefinition } from './types.js';

export const readFileTool: ToolDefinition = {
  spec: {
    name: 'read_file',
    description: 'Read the contents of a file. Can optionally read specific line ranges.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Absolute or relative path to the file',
        },
        start_line: {
          type: 'number',
          description: 'Line number to start reading from (1-indexed, optional)',
        },
        end_line: {
          type: 'number',
          description: 'Line number to stop reading at (1-indexed, optional)',
        },
      },
      required: ['path'],
    },
  },
  execute: async (input) => {
    const filePath = path.resolve(input['path'] as string);
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      // A trailing newline terminates the last line, it does not start a new one
      const lines = content.split('\n');
      if (lines[lines.length - 1] === '') lines.pop();
      const total = lines.length;

      // Clamp rather than let out-of-range values become negative slice
      // indices, which silently return lines from the end of the file
      const rawStart = (input['start_line'] as number | undefined) ?? 1;
      const rawEnd = (input['end_line'] as number | undefined) ?? total;
      const startLine = Math.max(1, Math.trunc(rawStart));
      const endLine = Math.min(total, Math.trunc(rawEnd));

      if (total === 0) return `File: ${filePath} (empty)`;
      if (startLine > total) {
        return `Error: start_line ${startLine} is past the end of ${filePath} (${total} lines)`;
      }
      if (startLine > endLine) {
        return `Error: start_line ${startLine} is after end_line ${endLine} in ${filePath}`;
      }

      const selectedLines = lines.slice(startLine - 1, endLine);
      const numbered = selectedLines
        .map((line, i) => `${(startLine + i).toString().padStart(4, ' ')}\t${line}`)
        .join('\n');
      return `File: ${filePath} (lines ${startLine}-${endLine} of ${total})\n\n${numbered}`;
    } catch (err) {
      const error = err as NodeJS.ErrnoException;
      return `Error reading file: ${error.message}`;
    }
  },
};

export const writeFileTool: ToolDefinition = {
  spec: {
    name: 'write_file',
    description: 'Write content to a file, creating it or overwriting it entirely.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to write to',
        },
        content: {
          type: 'string',
          description: 'Content to write',
        },
      },
      required: ['path', 'content'],
    },
  },
  execute: async (input) => {
    const filePath = path.resolve(input['path'] as string);
    const content = input['content'] as string;
    try {
      await fs.mkdir(path.dirname(filePath), { recursive: true });
      await fs.writeFile(filePath, content, 'utf-8');
      const lines = content.split('\n').length;
      return `Written ${lines} lines to ${filePath}`;
    } catch (err) {
      const error = err as NodeJS.ErrnoException;
      return `Error writing file: ${error.message}`;
    }
  },
};

export const editFileTool: ToolDefinition = {
  spec: {
    name: 'edit_file',
    description: 'Perform a targeted string replacement in a file. Use this for surgical edits without rewriting the whole file.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to the file',
        },
        old_string: {
          type: 'string',
          description: 'Exact string to replace (must be unique in the file)',
        },
        new_string: {
          type: 'string',
          description: 'Replacement string',
        },
        replace_all: {
          type: 'boolean',
          description: 'Replace all occurrences (default: false)',
        },
      },
      required: ['path', 'old_string', 'new_string'],
    },
  },
  execute: async (input) => {
    const filePath = path.resolve(input['path'] as string);
    const oldStr = input['old_string'] as string;
    const newStr = input['new_string'] as string;
    const replaceAll = (input['replace_all'] as boolean | undefined) ?? false;
    try {
      let content = await fs.readFile(filePath, 'utf-8');
      const occurrences = content.split(oldStr).length - 1;
      if (occurrences === 0) {
        return `Error: string not found in ${filePath}`;
      }
      if (!replaceAll && occurrences > 1) {
        return `Error: found ${occurrences} occurrences of the string in ${filePath}. Use replace_all: true or provide more context to make it unique.`;
      }
      // Never use String.replace with a string replacement: `$&`, `$1`, "$`"
      // etc. in new_string would be expanded instead of inserted literally
      if (replaceAll) {
        content = content.split(oldStr).join(newStr);
      } else {
        const at = content.indexOf(oldStr);
        content = content.slice(0, at) + newStr + content.slice(at + oldStr.length);
      }
      await fs.writeFile(filePath, content, 'utf-8');
      return `Replaced ${replaceAll ? occurrences : 1} occurrence(s) in ${filePath}`;
    } catch (err) {
      const error = err as NodeJS.ErrnoException;
      return `Error editing file: ${error.message}`;
    }
  },
};

export const listFilesTool: ToolDefinition = {
  spec: {
    name: 'list_files',
    description: 'List files in a directory or matching a glob pattern.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Directory path or glob pattern (e.g. "src/**/*.ts")',
        },
        include_hidden: {
          type: 'boolean',
          description: 'Include hidden files/dirs (default: false)',
        },
      },
      required: ['path'],
    },
  },
  execute: async (input) => {
    const inputPath = input['path'] as string;
    const includeHidden = (input['include_hidden'] as boolean | undefined) ?? false;

    try {
      const isGlob = inputPath.includes('*') || inputPath.includes('?');
      if (isGlob) {
        const files = await glob(inputPath, { dot: includeHidden });
        return files.length > 0
          ? files.sort().join('\n')
          : 'No files matched the pattern';
      }

      const resolvedPath = path.resolve(inputPath);
      const stat = await fs.stat(resolvedPath);

      if (stat.isFile()) {
        return resolvedPath;
      }

      const entries = await fs.readdir(resolvedPath, { withFileTypes: true });
      const filtered = includeHidden
        ? entries
        : entries.filter(e => !e.name.startsWith('.'));

      const lines = filtered
        .sort((a, b) => {
          if (a.isDirectory() !== b.isDirectory()) return a.isDirectory() ? -1 : 1;
          return a.name.localeCompare(b.name);
        })
        .map(e => `${e.isDirectory() ? '📁' : '📄'} ${e.name}${e.isDirectory() ? '/' : ''}`);

      return `${resolvedPath}/\n${lines.join('\n')}`;
    } catch (err) {
      const error = err as NodeJS.ErrnoException;
      return `Error listing files: ${error.message}`;
    }
  },
};

export const deleteFileTool: ToolDefinition = {
  spec: {
    name: 'delete_file',
    description: 'Delete a file or empty directory.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to delete',
        },
      },
      required: ['path'],
    },
  },
  execute: async (input) => {
    const filePath = path.resolve(input['path'] as string);
    try {
      await fs.rm(filePath, { recursive: false });
      return `Deleted: ${filePath}`;
    } catch (err) {
      const error = err as NodeJS.ErrnoException;
      return `Error deleting: ${error.message}`;
    }
  },
};
