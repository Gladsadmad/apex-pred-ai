import type { Tool } from '@anthropic-ai/sdk/resources/messages.js';

export interface ToolResult {
  type: 'tool_result';
  tool_use_id: string;
  content: string;
  is_error?: boolean;
}

export interface ToolExecutor {
  (input: Record<string, unknown>): Promise<string>;
}

export interface ToolDefinition {
  spec: Tool;
  execute: ToolExecutor;
}

export type ToolRegistry = Map<string, ToolDefinition>;
