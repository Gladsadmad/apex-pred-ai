import fetch from 'node-fetch';
import type { ToolDefinition } from './types.js';

export const webFetchTool: ToolDefinition = {
  spec: {
    name: 'web_fetch',
    description: 'Fetch the content of a URL. Returns the text content.',
    input_schema: {
      type: 'object',
      properties: {
        url: {
          type: 'string',
          description: 'The URL to fetch',
        },
        max_length: {
          type: 'number',
          description: 'Maximum characters to return (default: 10000)',
        },
      },
      required: ['url'],
    },
  },
  execute: async (input) => {
    const url = input['url'] as string;
    const maxLength = (input['max_length'] as number | undefined) ?? 10000;

    try {
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Apex-Pred-AI/1.0 (terminal assistant)',
        },
        signal: AbortSignal.timeout(15000),
      });

      if (!response.ok) {
        return `HTTP ${response.status}: ${response.statusText}`;
      }

      const contentType = response.headers.get('content-type') ?? '';
      const text = await response.text();

      if (contentType.includes('json')) {
        try {
          const parsed = JSON.parse(text);
          return JSON.stringify(parsed, null, 2).slice(0, maxLength);
        } catch {
          return text.slice(0, maxLength);
        }
      }

      const stripped = text
        .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
        .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
        .replace(/<[^>]+>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

      return stripped.slice(0, maxLength);
    } catch (err) {
      const error = err as { message: string };
      return `Fetch error: ${error.message}`;
    }
  },
};

export const webSearchTool: ToolDefinition = {
  spec: {
    name: 'web_search',
    description: 'Search the web using DuckDuckGo. Returns a summary of results with titles and snippets.',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query',
        },
        max_results: {
          type: 'number',
          description: 'Maximum number of results (default: 5)',
        },
      },
      required: ['query'],
    },
  },
  execute: async (input) => {
    const query = input['query'] as string;
    const maxResults = (input['max_results'] as number | undefined) ?? 5;

    try {
      const encoded = encodeURIComponent(query);
      const url = `https://api.duckduckgo.com/?q=${encoded}&format=json&no_html=1&skip_disambig=1`;
      const response = await fetch(url, {
        signal: AbortSignal.timeout(10000),
      });

      if (!response.ok) {
        return `Search failed: HTTP ${response.status}`;
      }

      const data = (await response.json()) as {
        AbstractText?: string;
        AbstractSource?: string;
        AbstractURL?: string;
        RelatedTopics?: Array<{
          Text?: string;
          FirstURL?: string;
          Topics?: Array<{ Text?: string; FirstURL?: string }>;
        }>;
      };

      const results: string[] = [];

      if (data.AbstractText) {
        results.push(`## Summary\n${data.AbstractText}\nSource: ${data.AbstractURL ?? data.AbstractSource}`);
      }

      if (data.RelatedTopics && results.length < maxResults) {
        const topics = data.RelatedTopics
          .flatMap(t => t.Topics ?? [t])
          .filter(t => t.Text && t.FirstURL)
          .slice(0, maxResults);

        for (const topic of topics) {
          results.push(`• ${topic.Text}\n  ${topic.FirstURL}`);
        }
      }

      if (results.length === 0) {
        return `No results found for: "${query}"\nTry web_fetch with a specific URL instead.`;
      }

      return results.join('\n\n');
    } catch (err) {
      const error = err as { message: string };
      return `Search error: ${error.message}`;
    }
  },
};
