import type { Tool, ToolResultBlockParam } from '@anthropic-ai/sdk/resources/messages.js';

// Re-export the SDK's own type to ensure perfect structural compatibility
// when tool results are passed back as MessageParam content
export type ToolResult = ToolResultBlockParam;

export interface ToolExecutor {
  (input: Record<string, unknown>): Promise<string>;
}

export interface ToolDefinition {
  spec: Tool;
  execute: ToolExecutor;
}

export type ToolRegistry = Map<string, ToolDefinition>;
