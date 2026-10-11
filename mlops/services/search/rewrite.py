from anthropic import AsyncAnthropic

from mlops.shared.config import settings


async def rewrite_query(query: str) -> str:
    if not settings.anthropic_api_key:
        return query
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=128,
        messages=[
            {
                "role": "user",
                "content": (
                    "Rewrite this ML experiment search query into a concise semantic search phrase. "
                    "Return only the rewritten query.\n\n"
                    f"{query}"
                ),
            }
        ],
    )
    block = response.content[0]
    text = getattr(block, "text", None)
    return text.strip() if isinstance(text, str) and text.strip() else query
