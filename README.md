# Mini Ahody — AI News Automation Pipeline

A working prototype that mirrors the core pipeline of editorial news automation platforms: **RSS feed ingestion → content extraction → AI article generation → publication-ready drafts.**

Built in Python with OpenAI's API, with deliberate focus on one of the hardest problems in newsroom AI: **hallucination control.**

---

## Why This Exists

Newsrooms can't manually monitor hundreds of sources 24/7. Stories get missed, publishing is slow, and scaling human editorial effort doesn't work. AI automation is the obvious answer — but "obvious" hides a hard problem: **if the AI invents facts, you've replaced slow journalism with fast misinformation.**

This prototype explores that specific trade-off at small scale.

---

## What It Does

`RSS Feed(s) → Fetch → Extract Content → Generate Draft → Save as Markdown`

- Pulls from **multiple RSS sources** in a single run (tested with BBC Tech + BBC World)
- Extracts clean article body text using BeautifulSoup (strips nav, footers, scripts)
- Sends structured input to OpenAI with a **journalist-style system prompt**
- Outputs a publication-ready draft with:
  - Suggested headline
  - SEO meta description (≤160 chars)
  - 3–5 paragraph article body
  - Source attribution
- Saves each draft as a timestamped `.md` file for easy review

---

## Design Decisions

### 1. Hallucination Control (the one that matters)

The system prompt explicitly instructs the model:

> *"If information is uncertain or missing, explicitly say 'according to reports' or 'reportedly'. Do not hallucinate missing details — flag them instead of inventing them."*

Combined with a low `temperature=0.3`, this produces output that flags uncertainty linguistically instead of confidently making things up. Sample output shows phrases like *"reportedly able to identify vulnerabilities"* and *"the discussions reportedly focused on..."* — the model hedged exactly where a careful journalist would.

This is not a full fact-checking system. It is a first-line defense against the most common failure mode in newsroom AI: confident fabrication.

### 2. Multi-Source Architecture

The pipeline runs each source independently in a loop, so one broken feed doesn't take down the whole run. This mirrors real production needs where sources fail silently (site redesigns, rate limits, timeouts).

### 3. Content Extraction Before Generation

The pipeline strips `<nav>`, `<footer>`, `<header>`, and `<script>` tags before sending content to the LLM. Small detail, significant impact on output quality.

### 4. Structured Output Format

The model is instructed to return sections labeled `HEADLINE`, `META DESCRIPTION`, `ARTICLE BODY`, `SOURCE`. Structured output is easier to parse downstream into CMS fields.

### 5. Local Markdown Storage

Drafts are saved as timestamped `.md` files. In production this would be a database or CMS push; in prototype form, markdown is human-reviewable and version-controllable.

---

## Sample Output

See `draft_*.md` files in this repo for real generated examples, including articles on:

- Anthropic / White House AI meeting (BBC Tech)
- Tinder / Zoom eye-scan verification (BBC Tech)
- Australian war crime soldier story (BBC World)

---

## Stack

- **Python 3.13**
- `openai` — LLM API client
- `feedparser` — RSS feed parsing
- `requests` + `beautifulsoup4` — content extraction
- `python-dotenv` — secret management
- Model: `gpt-4o-mini` (cost-efficient, sufficient for prose generation)

---

## Running It

pip install openai feedparser python-dotenv requests beautifulsoup4

Create a `.env` file with your OpenAI key:

Then:

---

## What's Missing (Honest Gaps)

This is a prototype, not production. A real version would need:

- **Retry logic** for failed API calls and timeouts
- **Deduplication** across RSS runs (currently re-processes same articles)
- **Async processing** — currently single-threaded, slow at scale
- **Proper fact-checking** — cross-referencing claims against primary sources
- **Caching layer** to avoid re-generating identical content
- **Source reliability monitoring** — detecting when a scraper silently breaks
- **Multi-language support** — tested only in English
- **Observability** — logging, metrics, cost tracking per article

These aren't bugs; they're the next design problems.

---

## Why I Built This

I'm applying for an AI & Backend Engineer role at Ahody Labs. Instead of listing skills on a CV, I wanted to show how I think about the problems Ahody is actually solving — specifically hallucination risk, source reliability, and pipeline design. This small prototype is the evidence.

Built over one weekend. Not polished, but working.

---

**Arjun Ponnaganti**
MSc AI/ML, Uppsala University
[github.com/AIArjun](https://github.com/AIArjun)
[arjunworks.se](https://arjunworks.se)
