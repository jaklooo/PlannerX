"""News/RSS feed service with AI summarization."""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from flask import current_app

logger = logging.getLogger(__name__)


def get_rss_feeds() -> List[Dict[str, str]]:
    """Load RSS feeds from YAML file."""
    try:
        import yaml
        feeds_file = Path(current_app.config.get("RSS_FEEDS_FILE"))

        if not feeds_file.exists():
            logger.warning(f"RSS feeds file not found: {feeds_file}")
            return []

        with open(feeds_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("feeds", [])
    except Exception as e:
        logger.error(f"Failed to load RSS feeds: {e}")
        return []


def fetch_news(max_items: int = 5, cache_hours: int = 12, fetch_all: bool = False) -> List[Dict[str, str]]:
    """
    Fetch news from RSS feeds with caching.

    Args:
        max_items: Maximum number of news items to return
        cache_hours: Cache validity in hours
        fetch_all: If True, fetch more items for AI processing

    Returns:
        List of news items with title, summary, link, published
    """
    try:
        import feedparser

        cache_file = Path(current_app.config.get("RSS_CACHE_FILE"))
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Check cache (but skip for fetch_all mode)
        if not fetch_all and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=cache_hours):
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    logger.info(f"Using cached news ({len(cached)} items)")
                    return cached[:max_items]

        # Fetch fresh news
        feeds = get_rss_feeds()
        all_entries = []
        seen_urls = set()

        # Fetch more items when doing AI processing
        items_per_feed = 50 if fetch_all else 3

        for feed_info in feeds:
            url = feed_info.get("url")
            if not url:
                continue

            try:
                logger.info(f"Fetching RSS feed: {url}")
                feed = feedparser.parse(url)

                for entry in feed.entries[:items_per_feed]:
                    link = entry.get("link", "")

                    # Deduplicate by URL
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)

                    # Extract summary (first sentence or description)
                    summary = entry.get("summary", entry.get("description", ""))
                    if summary:
                        # Get first sentence
                        import re
                        # Remove HTML tags
                        summary = re.sub(r"<[^>]+>", "", summary)
                        sentences = re.split(r"(?<=[.!?])\s+", summary)
                        summary = sentences[0] if sentences else summary
                        summary = summary[:300] + "..." if len(summary) > 300 else summary

                    # Get full content if available (for AI processing)
                    full_content = ""
                    if hasattr(entry, 'content') and entry.content:
                        full_content = entry.content[0].value if isinstance(entry.content, list) else str(entry.content)
                        full_content = re.sub(r"<[^>]+>", "", full_content)[:5000]  # Increased limit for richer content

                    all_entries.append({
                        "title": entry.get("title", "No title"),
                        "summary": summary,
                        "content": full_content,
                        "link": link,
                        "published": entry.get("published", ""),
                        "source": feed_info.get("name", url),
                    })

            except Exception as e:
                logger.error(f"Failed to fetch feed {url}: {e}")
                continue

        # Sort by published date (newest first)
        all_entries.sort(
            key=lambda x: x.get("published", ""),
            reverse=True
        )

        # Cache results
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(all_entries, f, ensure_ascii=False, indent=2)

        logger.info(f"Fetched {len(all_entries)} news items from {len(feeds)} feeds")
        return all_entries[:max_items] if not fetch_all else all_entries

    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        return []


def summarize_news_with_ai(news_items: List[Dict[str, str]], max_summary_items: int = 5) -> str:
    """
    Create AI-powered summary of news items.

    Args:
        news_items: List of news items (can be hundreds)
        max_summary_items: How many top stories to include in summary

    Returns:
        AI-generated summary text
    """
    if not news_items:
        return "Žiadne novinky nie sú k dispozícii."

    try:
        # Step 1: Extract titles for initial ranking
        titles = [item['title'] for item in news_items[:200]]  # Limit to 200 for processing

        # Step 2: AI ranking by importance
        ranked_items = rank_news_by_importance(titles, news_items[:200])

        # Step 3: Get top N items with full content
        top_items = ranked_items[:max_summary_items]

        # Step 4: Generate detailed summary
        return generate_news_summary(top_items)

    except Exception as e:
        logger.error(f"AI summarization failed: {e}")
        # Fallback to simple summary
        return summarize_news_simple(news_items[:max_summary_items])


def rank_news_by_importance(titles: List[str], news_items: List[Dict]) -> List[Dict]:
    """
    Use AI to rank news by importance based on titles.

    Args:
        titles: List of news titles
        news_items: Corresponding news items

    Returns:
        Ranked list of news items
    """
    try:
        import openai

        api_key = current_app.config.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not configured, using simple ranking")
            return news_items[:10]  # Return first 10 as fallback

        client = openai.OpenAI(api_key=api_key)

        prompt = f"""
        Here are news headlines from today. Rank them by importance/relevance for a Slovak user.
        Consider:
        - Slovakia/EU related news
        - Major world events
        - Economic/political impact
        - Breaking news vs routine updates

        Headlines:
        {chr(10).join(f"{i+1}. {title}" for i, title in enumerate(titles))}

        Return only a JSON array of indices (0-based) in order of importance, max 10 items:
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3
        )

        result = response.choices[0].message.content.strip()

        # Parse JSON response
        try:
            indices = json.loads(result)
            if isinstance(indices, list):
                ranked_items = [news_items[i] for i in indices if i < len(news_items)]
                return ranked_items
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI ranking response: {result}")

        # Fallback: return first 10 items
        return news_items[:10]

    except ImportError:
        logger.warning("OpenAI library not installed, using simple ranking")
        return news_items[:10]
    except Exception as e:
        logger.error(f"AI ranking failed: {e}")
        return news_items[:10]


def generate_news_summary(news_items: List[Dict]) -> str:
    """
    Generate detailed AI summary of top news items.

    Args:
        news_items: Top news items with full content

    Returns:
        Formatted summary text
    """
    try:
        import openai

        api_key = current_app.config.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not configured, using simple summary")
            return summarize_news_simple(news_items)

        client = openai.OpenAI(api_key=api_key)

        # Prepare content for AI
        news_text = ""
        for i, item in enumerate(news_items, 1):
            news_text += f"""
            {i}. {item['title']}
            Source: {item.get('source', 'Unknown')}
            Summary: {item.get('summary', 'No summary')}
            Content: {item.get('content', 'No full content')[:2000]}
            """

        prompt = f"""
        Create a comprehensive and informative summary of today's top news stories for a Slovak user.
        Focus on the most important developments, their implications, and provide rich context.

        News stories:
        {news_text}

        Provide a detailed summary in Slovak language, structured as:
        1. **Najdôležitejšie udalosti** - prehľad kľúčových správ s dôrazom na dopady
        2. **Detailnejšie informácie** - rozvinutie najdôležitejších tém s kontextom a súvislosťami
        3. **Trendy a súvislosti** - aké väčšie trendy alebo súvislosti tieto správy naznačujú

        Be objective, factual, and provide meaningful insights. Include specific details, numbers, and implications where relevant.
        Keep it under 800 words but be comprehensive rather than brief.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Better model for richer, more comprehensive summaries
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,  # Increased for richer summaries
            temperature=0.4
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except ImportError:
        logger.warning("OpenAI library not installed, using simple summary")
        return summarize_news_simple(news_items)
    except Exception as e:
        logger.error(f"AI summary generation failed: {e}")
        return summarize_news_simple(news_items)


def summarize_news_simple(news_items: List[Dict[str, str]]) -> str:
    """
    Create a simple text summary of news items (fallback).

    Args:
        news_items: List of news items

    Returns:
        Formatted text summary
    """
    if not news_items:
        return "Žiadne novinky nie sú k dispozícii."

    lines = ["**Dnešné najdôležitejšie správy:**"]
    for i, item in enumerate(news_items, 1):
        lines.append(f"{i}. **{item['title']}**")
        if item.get("summary"):
            lines.append(f"   {item['summary']}")
        lines.append("")

    return "\n".join(lines)


def summarize_news(news_items: List[Dict[str, str]]) -> str:
    """
    Legacy function - now uses AI summarization.

    Args:
        news_items: List of news items

    Returns:
        Formatted text summary
    """
    return summarize_news_with_ai(news_items)
