"""
Mini Ahody — AI News Automation Pipeline
Built by Arjun Ponnaganti | arjunworks.se
A miniature version of Ahody's core pipeline:
RSS Feed -> Fetch -> Extract -> Summarize with AI -> Ready-to-publish draft
"""

import os
import feedparser
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fetch_rss_feed(feed_url, max_articles=3):
    """Fetch the latest articles from an RSS feed."""
    print(f"\n[1/4] Fetching RSS feed from: {feed_url}")
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        print("No articles found in feed.")
        return []
    
    articles = []
    for entry in feed.entries[:max_articles]:
        articles.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "published": entry.get("published", "Unknown date"),
            "summary": entry.get("summary", "")
        })
    
    print(f"Found {len(articles)} article(s).")
    return articles


def extract_article_content(url):
    """Extract clean article text from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get paragraph text
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40])
        
        return text[:3000]  # limit to 3000 chars to control API cost
    except Exception as e:
        print(f"Error extracting content: {e}")
        return ""


def generate_article_draft(title, content, source_url):
    """Use OpenAI to generate a journalist-style article draft."""
    print(f"[3/4] Generating AI draft for: {title[:60]}...")
    
    system_prompt = """You are a professional editorial assistant for a newsroom.
Your job is to take raw news content and transform it into a clean, ready-to-publish article draft.

Rules:
- Write in neutral, journalistic tone
- Start with a strong lead paragraph (who, what, when, where, why)
- Use short paragraphs (2-3 sentences max)
- Include a clear headline suggestion
- Add a one-line SEO meta description
- Never invent facts - only use information from the source
- If information is uncertain or missing, explicitly say "according to reports" or "reportedly"
- Do not hallucinate missing details - flag them instead of inventing them
- End with the source attribution"""
    
    user_prompt = f"""Original Title: {title}
Source URL: {source_url}

Raw Content:
{content}

Generate a clean article draft with:
1. HEADLINE: (suggested new headline)
2. META DESCRIPTION: (one line, SEO-friendly, max 160 chars)
3. ARTICLE BODY: (3-5 short paragraphs)
4. SOURCE: (attribution line)"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature = more factual, less creative
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating draft: {e}")
        return None


def save_draft_to_file(draft, title):
    """Save the generated draft to a markdown file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in title if c.isalnum() or c == " ")[:50].strip().replace(" ", "_")
    filename = f"draft_{timestamp}_{safe_title}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(draft)
    
    return filename


def run_pipeline(rss_url, max_articles=2):
    """Main pipeline: fetch -> extract -> generate -> save."""
    print("=" * 60)
    print("MINI AHODY - AI News Automation Pipeline")
    print("Built by Arjun Ponnaganti | AI News Automation Demo")
    print("Inspired by Ahody Labs")
    print("=" * 60)
    
    # Step 1: Fetch RSS
    articles = fetch_rss_feed(rss_url, max_articles)
    if not articles:
        return
    
    # Step 2-4: Process each article
    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i}/{len(articles)} ---")
        print(f"[2/4] Extracting content from: {article['link']}")
        
        content = extract_article_content(article["link"])
        if not content:
            print("Skipping - no content extracted.")
            continue
        
        print(f"Extracted {len(content)} characters.")
        
        # Generate AI draft
        draft = generate_article_draft(article["title"], content, article["link"])
        if not draft:
            continue
        
        # Save to file
        filename = save_draft_to_file(draft, article["title"])
        print(f"[4/4] Saved draft to: {filename}")
        print("\n" + "-" * 60)
        print("DRAFT PREVIEW:")
        print("-" * 60)
        print(draft)
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print(f"Pipeline complete. Processed {len(articles)} article(s).")
    print("=" * 60)


if __name__ == "__main__":
    # Multi-source ingestion - mirrors Ahody's approach of monitoring multiple sources
    DEFAULT_FEEDS = [
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "http://feeds.bbci.co.uk/news/world/rss.xml"
    ]
    
    print("\nEnter RSS feed URL (press Enter to use multi-source default: BBC Tech + BBC World):")
    user_input = input("> ").strip()
    
    print("\nHow many articles PER SOURCE? (default: 1)")
    num_input = input("> ").strip()
    num_articles = int(num_input) if num_input.isdigit() else 1
    
    if user_input:
        # User gave a single feed
        run_pipeline(user_input, num_articles)
    else:
        # Multi-source mode
        print(f"\n[MULTI-SOURCE MODE] Processing {len(DEFAULT_FEEDS)} feeds...")
        for i, feed in enumerate(DEFAULT_FEEDS, 1):
            print(f"\n>>> SOURCE {i}/{len(DEFAULT_FEEDS)} <<<")
            run_pipeline(feed, num_articles)
        
        print("\n" + "=" * 60)
        print(f"ALL SOURCES COMPLETE. Processed {len(DEFAULT_FEEDS)} feeds.")
        print("=" * 60)