# AI Agent Portfolio - Demo Guide

This portfolio contains 3 "Ready-to-Deploy" AI Agents designed for real business use cases. Use these scripts to record your demos.

## 1. Real Estate WhatsApp Matcher
**Business Task:** WhatsApp bot, Property Matcher
**Description:** Simulates a WhatsApp Business chatbot that qualifies buyers and finds properties using live data.
**How to Run:**
```bash
cd agents/real-estate
python whatsapp_bot.py
```
**Demo Flow:**
1. Bot says "Hi, I'm Sarah..."
2. You type: "Bangalore"
3. Bot asks property type -> You type: "Flat"
4. Bot asks budget -> You type: "3.5"
5. Bot searches (10-15s) and returns real listings.
6. You ask to book a visit -> Bot captures lead.

## 2. Inbound Sales Receptionist
**Business Task:** Lead Qualification, Appointment Setting
**Description:** A voice/chat-capable receptionist that qualifies inbound leads and saves them to a CRM.
**How to Run:**
```bash
cd agents/sales
python lead_qualifier.py
```
**Demo Flow:**
1. Bot asks "How can I help?"
2. You: "I'm interested in your marketing services."
3. Bot asks for name -> You: "John Doe"
4. Bot asks budget -> You: "Around $2000/month"
5. Bot asks phone -> You: "555-0123"
6. Bot saves lead to `leads_db.json` and closes the call.

## 3. Automated Content Engine
**Business Task:** Content Pipeline, Social Media Automation
**Description:** A CrewAI team (Researcher, Strategist, Writer) that takes a topic and generates ready-to-post content.
**How to Run:**
```bash
cd agents/social_media
python content_engine.py
```
**Demo Flow:**
1. Script asks for topic.
2. You type: "Impact of AI on Real Estate"
3. Watch the agents work in the terminal (Researching -> Strategizing -> Writing).
4. Final output: 3 high-quality LinkedIn posts.
5. Content saved to a `.txt` file.

## Prerequisites
Ensure your `.env` file in the root directory has:
- `OPENAI_API_KEY`
- `FIRECRAWL_API_KEY` (for Real Estate)
- `SERPER_API_KEY` (for Content Engine)
