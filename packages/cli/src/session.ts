import fs from 'fs/promises';
import path from 'path';
import type { MessageParam } from '@anthropic-ai/sdk/resources/messages.js';

export interface Session {
  id: string;
  createdAt: string;
  updatedAt: string;
  messages: MessageParam[];
  metadata: {
    model: string;
    totalTokensUsed: number;
  };
}

export class SessionManager {
  private session: Session;
  private historyDir: string;

  constructor(historyDir: string, model: string) {
    this.historyDir = historyDir;
    this.session = {
      id: this.generateId(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [],
      metadata: {
        model,
        totalTokensUsed: 0,
      },
    };
  }

  private generateId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  }

  addMessage(message: MessageParam): void {
    this.session.messages.push(message);
    this.session.updatedAt = new Date().toISOString();
  }

  getMessages(): MessageParam[] {
    return this.session.messages;
  }

  clearMessages(): void {
    this.session.messages = [];
    this.session.updatedAt = new Date().toISOString();
  }

  updateTokenUsage(tokens: number): void {
    this.session.metadata.totalTokensUsed += tokens;
  }

  getTokenUsage(): number {
    return this.session.metadata.totalTokensUsed;
  }

  getSessionId(): string {
    return this.session.id;
  }

  async save(): Promise<void> {
    try {
      await fs.mkdir(this.historyDir, { recursive: true });
      const filePath = path.join(this.historyDir, `${this.session.id}.json`);
      await fs.writeFile(filePath, JSON.stringify(this.session, null, 2), 'utf-8');
    } catch {
      // Non-fatal: session saving is best-effort
    }
  }

  static async listSessions(historyDir: string): Promise<string[]> {
    try {
      const files = await fs.readdir(historyDir);
      return files.filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''));
    } catch {
      return [];
    }
  }

  static async loadSession(historyDir: string, sessionId: string): Promise<Session | null> {
    try {
      const filePath = path.join(historyDir, `${sessionId}.json`);
      const content = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(content) as Session;
    } catch {
      return null;
    }
  }
}
