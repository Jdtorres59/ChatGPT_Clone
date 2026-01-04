# ChatGPT Clone

## Project Overview
ChatGPT Clone is a lightweight Flask app that wraps the OpenAI API with a clean, modern chat UI.
It is designed as a portfolio-ready devtool that highlights product polish and cost controls.
The experience is focused on a single flow: prompt, response, and clear system feedback.

## Why I Built This
I wanted a compact project that shows full-stack ownership, from UI polish to backend guardrails.
It also demonstrates how to ship a public demo responsibly without exposing runaway costs.

## Key Features
- Modern chat UI with empty, loading, and error states
- Sticky composer with keyboard shortcuts (Enter to send, Shift+Enter for new line)
- In-memory demo limits (per IP, global daily, cooldown) with 429 responses
- Token cap on responses to control spend
- Clear chat and copy last answer utilities
- Responsive layout that works on desktop and mobile

## Tech Stack
- Python
- Flask
- OpenAI API
- HTML, CSS, JavaScript

## High-Level How It Works
The browser sends user prompts to a Flask endpoint via a simple GET request.
The server applies demo limits (IP and global) before calling the OpenAI API.
Responses are capped by max tokens and returned to the client as plain text.
The UI renders messages as chat bubbles and surfaces loading or error states.
A lightweight in-memory store tracks daily usage and resets each day.

## What I Learned
- How to design guardrails for public demos without adding heavy infrastructure
- Building a modern UI with clear UX states and accessibility hints
- Balancing product polish with pragmatic backend constraints
- Communicating cost and security tradeoffs directly in the interface

## Status
Active - portfolio demo ready.

## Demo
Live demo: https://chatgpt-clone-rp4j.onrender.com
This public demo is rate-limited to control costs (5 requests/day per IP, 50/day total, 15s cooldown).
To run unlimited, clone the repo and set `OPENAI_API_KEY` locally.
