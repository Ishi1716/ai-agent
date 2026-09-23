# 🤖 My AI Agent

A beginner-friendly AI Agent built with Python, Google Gemini API, Streamlit, RAG, tools, and conversation memory.

## 🚀 Features

- 🤖 Gemini AI integration
- 🧮 Calculator tool
- 🕐 Current time tool
- 📚 PDF question answering
- 🔎 TF-IDF based RAG
- 🧠 Conversation memory
- 💬 Streamlit chat interface
- 🛠️ Intelligent tool selection
- ⚠️ API error and rate-limit handling

## 🧠 Architecture

```text
                    User
                      │
                      ▼
                Streamlit UI
                      │
                      ▼
               Agent Planner
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Calculator    Current Time    PDF / RAG
        │             │             │
        │             │        PDF Reader
        │             │             │
        │             │          Chunking
        │             │             │
        │             │        TF-IDF Search
        │             │             │
        └─────────────┴─────────────┘
                      │
                      ▼
                 Gemini API
                      │
                      ▼
                 AI Response
                      │
                      ▼
                Conversation
                   Memory