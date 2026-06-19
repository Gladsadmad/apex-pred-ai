import Anthropic from '@anthropic-ai/sdk';
import type {
  ContentBlock,
  TextBlock,
  ToolUseBlock,
} from '@anthropic-ai/sdk/resources/messages.js';
import ora from 'ora';
import process from 'process';
import { theme } from './ui/theme.js';
import { renderMarkdown, renderToolCall } from './ui/renderer.js';
import { APEX_PRED_SYSTEM_PROMPT } from './personality.js';
import { createToolRegistry, getToolSpecs } from './tools/index.js';
import type { ToolResult } from './tools/types.js';
import type { ApexConfig } from './config.js';
import { SessionManager } from './session.js';

export class ApexPredAgent {
  private client: Anthropic;
  private config: ApexConfig;
  private tools = createToolRegistry();
  private session: SessionManager;

  constructor(config: ApexConfig) {
    this.config = config;

    if (!config.apiKey) {
      console.error(theme.error('No API key found. Set ANTHROPIC_API_KEY or run: apex config --key YOUR_KEY'));
      process.exit(1);
    }

    this.client = new Anthropic({ apiKey: config.apiKey });
    this.session = new SessionManager(config.sessionHistoryDir, config.model);
  }

  async chat(userMessage: string): Promise<void> {
    this.session.addMessage({ role: 'user', content: userMessage });

    await this.runAgentLoop();
    await this.session.save();
  }

  private async runAgentLoop(): Promise<void> {
    while (true) {
      const spinner = ora({
        text: theme.muted('Apex-Pred is thinking...'),
        spinner: 'dots',
        color: 'red',
      }).start();

      try {
        const response = await this.client.messages.create({
          model: this.config.model,
          max_tokens: this.config.maxTokens,
          system: APEX_PRED_SYSTEM_PROMPT,
          messages: this.session.getMessages(),
          tools: getToolSpecs(this.tools),
        });

        spinner.stop();

        this.session.updateTokenUsage(response.usage.input_tokens + response.usage.output_tokens);

        const assistantContent = response.content;
        this.session.addMessage({ role: 'assistant', content: assistantContent });

        const textBlocks = assistantContent.filter((b): b is TextBlock => b.type === 'text');
        const toolBlocks = assistantContent.filter((b): b is ToolUseBlock => b.type === 'tool_use');

        if (textBlocks.length > 0) {
          const text = textBlocks.map(b => b.text).join('\n');
          process.stdout.write('\n' + theme.aiLabel());
          process.stdout.write(renderMarkdown(text));
          process.stdout.write('\n');
        }

        if (response.stop_reason === 'end_turn' || toolBlocks.length === 0) {
          break;
        }

        const toolResults = await this.executeTools(toolBlocks);

        this.session.addMessage({
          role: 'user',
          content: toolResults,
        });
      } catch (err) {
        spinner.stop();
        const error = err as { message: string; status?: number };

        if (error.status === 401) {
          console.error(theme.error('\nInvalid API key. Check your ANTHROPIC_API_KEY.'));
        } else if (error.status === 429) {
          console.error(theme.error('\nRate limit hit. Slow your roll for a sec.'));
        } else {
          console.error(theme.error(`\nAPI error: ${error.message}`));
        }
        break;
      }
    }
  }

  private async executeTools(toolBlocks: ToolUseBlock[]): Promise<ToolResult[]> {
    const results: ToolResult[] = [];

    for (const block of toolBlocks) {
      const toolDef = this.tools.get(block.name);

      console.log('\n' + renderToolCall(block.name, block.input as Record<string, unknown>));

      if (!toolDef) {
        results.push({
          type: 'tool_result',
          tool_use_id: block.id,
          content: `Unknown tool: ${block.name}`,
          is_error: true,
        });
        continue;
      }

      const toolSpinner = ora({
        text: theme.muted(`Running ${block.name}...`),
        spinner: 'line',
        color: 'yellow',
      }).start();

      try {
        const result = await toolDef.execute(block.input as Record<string, unknown>);
        toolSpinner.stop();

        if (this.config.debug) {
          console.log(theme.muted(`  → ${result.slice(0, 200)}${result.length > 200 ? '...' : ''}`));
        }

        results.push({
          type: 'tool_result',
          tool_use_id: block.id,
          content: result,
        });
      } catch (err) {
        toolSpinner.stop();
        const error = err as { message: string };
        const errorMsg = `Tool execution failed: ${error.message}`;
        console.error(theme.error(`  ✗ ${errorMsg}`));

        results.push({
          type: 'tool_result',
          tool_use_id: block.id,
          content: errorMsg,
          is_error: true,
        });
      }
    }

    return results;
  }

  async streamingChat(userMessage: string): Promise<void> {
    this.session.addMessage({ role: 'user', content: userMessage });
    await this.runStreamingAgentLoop();
    await this.session.save();
  }

  private async runStreamingAgentLoop(): Promise<void> {
    while (true) {
      process.stdout.write('\n' + theme.aiLabel());

      const collectedContent: ContentBlock[] = [];
      let fullText = '';

      try {
        const stream = await this.client.messages.stream({
          model: this.config.model,
          max_tokens: this.config.maxTokens,
          system: APEX_PRED_SYSTEM_PROMPT,
          messages: this.session.getMessages(),
          tools: getToolSpecs(this.tools),
        });

        for await (const chunk of stream) {
          if (chunk.type === 'content_block_delta' && chunk.delta.type === 'text_delta') {
            process.stdout.write(chunk.delta.text);
            fullText += chunk.delta.text;
          }
        }

        const finalMessage = await stream.finalMessage();
        process.stdout.write('\n');

        this.session.updateTokenUsage(
          finalMessage.usage.input_tokens + finalMessage.usage.output_tokens
        );
        this.session.addMessage({ role: 'assistant', content: finalMessage.content });

        const toolBlocks = finalMessage.content.filter(
          (b): b is ToolUseBlock => b.type === 'tool_use'
        );

        if (finalMessage.stop_reason === 'end_turn' || toolBlocks.length === 0) {
          break;
        }

        const toolResults = await this.executeTools(toolBlocks);
        this.session.addMessage({ role: 'user', content: toolResults });
      } catch (err) {
        const error = err as { message: string; status?: number };
        process.stdout.write('\n');

        if (error.status === 401) {
          console.error(theme.error('Invalid API key.'));
        } else {
          console.error(theme.error(`Stream error: ${error.message}`));
        }
        break;
      }

      void collectedContent;
      void fullText;
    }
  }

  clearSession(): void {
    this.session.clearMessages();
  }

  getSessionInfo(): { id: string; messageCount: number; tokensUsed: number } {
    return {
      id: this.session.getSessionId(),
      messageCount: this.session.getMessages().length,
      tokensUsed: this.session.getTokenUsage(),
    };
  }

  listTools(): string[] {
    return Array.from(this.tools.keys());
  }
}
