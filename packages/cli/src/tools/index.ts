import type { Tool } from '@anthropic-ai/sdk/resources/messages.js';
import type { ToolRegistry } from './types.js';
import { readFileTool, writeFileTool, editFileTool, listFilesTool, deleteFileTool } from './file.js';
import { bashTool } from './bash.js';
import { gitTool } from './git.js';
import { webFetchTool, webSearchTool } from './web.js';

export function createToolRegistry(): ToolRegistry {
  const registry: ToolRegistry = new Map();
  const tools = [
    readFileTool,
    writeFileTool,
    editFileTool,
    listFilesTool,
    deleteFileTool,
    bashTool,
    gitTool,
    webFetchTool,
    webSearchTool,
  ];

  for (const tool of tools) {
    registry.set(tool.spec.name, tool);
  }

  return registry;
}

export function getToolSpecs(registry: ToolRegistry): Tool[] {
  return Array.from(registry.values()).map(t => t.spec);
}

export { type ToolRegistry, type ToolResult } from './types.js';
