from __future__ import annotations

import json
import re
from typing import Any

import httpx
from anthropic.types import ToolParam


async def _web_fetch(url: str, max_length: int = 10000) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Apex-Pred-AI/1.0 (terminal assistant)"},
            )
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            text = response.text

            if "json" in content_type:
                try:
                    return json.dumps(json.loads(text), indent=2)[:max_length]
                except Exception:
                    return text[:max_length]

            stripped = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", text, flags=re.IGNORECASE)
            stripped = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", stripped, flags=re.IGNORECASE)
            stripped = re.sub(r"<[^>]+>", " ", stripped)
            stripped = re.sub(r"\s+", " ", stripped).strip()
            return stripped[:max_length]
    except Exception as e:
        return f"Fetch error: {e}"


async def _web_search(query: str, max_results: int = 5) -> str:
    try:
        encoded = query.replace(" ", "+")
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            data = response.json()

        results = []
        if data.get("AbstractText"):
            results.append(f"## Summary\n{data['AbstractText']}\nSource: {data.get('AbstractURL', '')}")

        topics = data.get("RelatedTopics", [])
        flat_topics = []
        for t in topics:
            if "Topics" in t:
                flat_topics.extend(t["Topics"])
            else:
                flat_topics.append(t)

        for topic in flat_topics[:max_results]:
            if topic.get("Text") and topic.get("FirstURL"):
                results.append(f"• {topic['Text']}\n  {topic['FirstURL']}")

        if not results:
            return f'No results for "{query}". Try web_fetch with a specific URL.'
        return "\n\n".join(results)
    except Exception as e:
        return f"Search error: {e}"


TOOL_HANDLERS: dict[str, Any] = {
    "web_fetch": _web_fetch,
    "web_search": _web_search,
}

web_tools: list[ToolParam] = [
    {
        "name": "web_fetch",
        "description": "Fetch the content of a URL. Returns text content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "max_length": {"type": "integer", "description": "Max characters to return (default: 10000)"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "web_search",
        "description": "Search the web using DuckDuckGo. Returns titles, snippets, and links.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Max results (default: 5)"},
            },
            "required": ["query"],
        },
    },
]
