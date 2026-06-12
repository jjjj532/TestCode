import httpx


async def web_fetch(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            import re
            text = resp.text
            text = re.sub(r'<[^>]+>', '', text)
            text = '\n'.join(line for line in text.split('\n') if line.strip())
            return text[:10000] if len(text) > 10000 else text
    except httpx.HTTPStatusError as e:
        return f"HTTP error: {e.response.status_code} {e.response.reason_phrase}"
    except Exception as e:
        return f"Error fetching URL: {e}"
