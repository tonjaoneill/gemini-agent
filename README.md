# Gemini Agent — Two Implementations, Side by Side

A local Python agent built on Google's Gemini API that autonomously reads text files, summarizes them, and maintains a running catalog — deciding for itself what needs summarizing, rather than following a fixed script.

This repo intentionally contains **two versions of the same agent**, built to directly compare a hand-written approach against a framework:

## `agent.py` — Hand-built
Writes the full tool-calling loop manually: JSON schema definitions for each tool, and an explicit `while`/`for` loop that checks the model's response, executes the matching Python function, and feeds the result back until the model produces a final answer.

## `langchain_agent.py` — LangChain version
The same four tools and the same task, rebuilt using the [LangChain](https://docs.langchain.com/) framework's `@tool` decorator and `create_agent()`, which handle schema generation and the request/response loop internally.

## Why both exist
Built the hand-written version first to understand exactly what a framework like LangChain automates under the hood, then rebuilt it with LangChain to compare directly — code volume, transparency, and when each approach is actually the better choice. (Short version: at this small scale, hand-built won on transparency and control; LangChain's advantage shows up with more tools, multiple model providers, or built-in memory/retry needs.)

## What the agent does
Given a folder of `.txt` articles (`~/Desktop/Articles`):
1. Reads the existing `catalog.md` to see what's already been summarized
2. Lists available `.txt` files
3. Reads and summarizes any file not yet in the catalog
4. Appends a new entry to `catalog.md` — skipping anything already processed

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install google-genai python-dotenv langchain langchain-google-genai
```

Create a `.env` file (not committed) with:
```
GEMINI_API_KEY=your_key_here
```

Then run either version:
```bash
python3 agent.py
python3 langchain_agent.py
```

**Note:** Gemini's free tier caps `gemini-3.6-flash` at 20 requests/day per project — shared across both scripts if you run them against the same key.