# DEV//SCOPE

### **Research before you reinvent.**

**DevScope** is a CLI-first developer research instrument that investigates existing open-source implementations before you build.

Give it an idea, and DevScope searches relevant GitHub projects, analyzes their implementations, compares approaches, identifies gaps, and surfaces opportunities to build something meaningfully different.

```text
Idea
 ↓
Open-source Discovery
 ↓
Repository Analysis
 ↓
Implementation Comparison
 ↓
Gap Detection
 ↓
Differentiation Opportunities
```

> **Don't just ask "Can I build this?"**
> Ask **"What already exists, what's missing, and how can I build it better?"**

---

## ✦ Why DevScope?

Developers often start building an idea without knowing how much of it already exists.

DevScope turns that research process into a repeatable workflow:

* 🔎 **Discover** relevant open-source implementations
* 🧠 **Analyze** repositories and their technical approaches
* ⚖️ **Compare** competing implementations
* 🕳️ **Identify gaps** and missing capabilities
* 💡 **Find differentiation opportunities**
* 📚 **Back conclusions with evidence**
* 🖥️ **Run locally** with Ollama — no paid LLM required

DevScope is designed for **developers, researchers, and builders validating technical ideas before implementation.**

---

## 🚀 Quick Start

### 1. Install

```powershell
pip install -e .
```

### 2. Initialize

```powershell
devscope init
```

### 3. Research an idea

```powershell
devscope research "An MCP-powered AI research agent"
```

DevScope will investigate the open-source landscape and produce an evidence-backed research report covering existing implementations, technical approaches, gaps, and potential differentiation.

---

# 🧩 What DevScope Does

A typical research workflow looks like:

```text
┌──────────────────────────────┐
│        Developer Idea        │
│ "MCP-powered AI agent"       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     Repository Discovery     │
│       GitHub Search           │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Repository Analysis     │
│ README • Code • Structure    │
│ Dependencies • Architecture  │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│        Comparison Engine     │
│ Features • Architecture      │
│ Implementation • Trade-offs  │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│        Gap Detection         │
│ Missing features & weaknesses│
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     Differentiation Ideas    │
│ "Here's where you can win."  │
└──────────────────────────────┘
```

---

# ⚡ Core Features

### 🔎 Open-Source Discovery

Searches GitHub for projects relevant to your idea instead of relying only on manually provided repositories.

### 🧠 Repository-Level Analysis

DevScope goes beyond repository names and descriptions.

It can reason about:

* Project architecture
* Technologies and frameworks
* Dependencies
* Features
* Implementation approaches
* Repository structure
* Documentation
* Project maturity

### ⚖️ Evidence-Backed Comparison

Compare multiple implementations based on what they **actually contain**, rather than making assumptions from project descriptions.

### 🕳️ Gap Detection

Identify areas where existing implementations are incomplete, limited, or leave room for improvement.

Examples:

```text
Existing projects:
✓ MCP support
✓ Local LLM
✓ GitHub integration

Observed gaps:
✗ No repository-level reasoning
✗ Limited extensibility
✗ No persistent research history
✗ Weak evidence tracking
```

### 💡 Differentiation Opportunities

The goal isn't simply to tell you what already exists.

DevScope helps answer:

> **"What can I build that is actually different?"**

---

# 🖥️ CLI-First

DevScope is designed around the command line.

```powershell
devscope research "A local AI code review agent"
```

Authenticate GitHub:

```powershell
devscope auth github
```

Start the MCP server:

```powershell
devscope mcp
```

Initialize a project:

```powershell
devscope init
```

The CLI is intended to make technical research feel like another developer tool rather than another web dashboard.

---

# 🤖 Local LLMs

DevScope defaults to **Ollama**, allowing the analysis pipeline to run locally without a paid LLM provider.

Install Ollama and pull the default model:

```powershell
ollama pull qwen2.5:7b
```

Then:

```powershell
devscope mcp
```

DevScope uses **Qwen 2.5 7B** by default because it provides stronger structured JSON generation and multi-step reasoning than smaller starter models.

Configure the model through `.env`:

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

You can replace the model with another locally served Ollama model.

> **Security note:** Repository content is treated as untrusted source material and should not be interpreted as trusted instructions by the model.

---

# 🐙 GitHub Integration

GitHub authentication is optional.

DevScope uses the following authentication order:

```text
GITHUB_TOKEN
      ↓
GitHub CLI session
      ↓
Unauthenticated public API
```

For the best rate limits without manually managing a token:

```powershell
gh auth login
```

Or allow DevScope to guide you through authentication:

```powershell
devscope auth github
```

This launches GitHub's browser/device authentication through the GitHub CLI.

DevScope reads the resulting local GitHub CLI session, so you don't need to place a `GITHUB_TOKEN` in `.env`.

---

# 🧠 MCP Support

DevScope can expose its research capabilities through **Model Context Protocol (MCP)**.

Start the MCP server:

```powershell
devscope mcp
```

This allows DevScope's research capabilities to be consumed by compatible MCP clients and AI workflows.

The architecture is intentionally designed around tools rather than a single hard-coded research flow.

---

# ✨ Gemini / Vertex AI

DevScope can also use Gemini through Google Vertex AI.

Authenticate using Google Cloud:

```powershell
devscope auth google --project YOUR_GOOGLE_CLOUD_PROJECT
```

This opens Google login through the Google Cloud CLI and stores short-lived credentials using Google's local application-default credential mechanism.

Then configure:

```env
LLM_PROVIDER=gemini
```

Your Google Cloud project must have:

* Vertex AI enabled
* Billing configured
* Appropriate quota/access

A normal consumer Google account login by itself is **not sufficient** for hosted Gemini API access.

---

# 🏗️ Architecture

At a high level:

```text
                    ┌───────────────┐
                    │   DevScope    │
                    │     CLI       │
                    └───────┬───────┘
                            │
                            ↓
                    ┌───────────────┐
                    │ Research      │
                    │ Orchestrator  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
        GitHub Search   Repository    Metadata
                         Analysis      Extraction
              │             │             │
              └─────────────┼─────────────┘
                            ↓
                    ┌───────────────┐
                    │ Evidence      │
                    │ Collection    │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ LLM Analysis  │
                    │ & Comparison  │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ Gap Detection │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ Differentiation│
                    │ Opportunities  │
                    └───────────────┘
```

---

# 📋 Example Research

```powershell
devscope research "An MCP-powered AI research agent"
```

Instead of simply returning a list of GitHub repositories, DevScope is intended to answer questions such as:

```text
What already exists?
        ↓
How do existing projects work?
        ↓
How are their approaches different?
        ↓
What capabilities are missing?
        ↓
Where are the technical weaknesses?
        ↓
What could make a new implementation different?
```

This makes DevScope useful during the **idea validation and technical research phase** of development.

---

# 🔐 Privacy & Authentication

DevScope is designed with local-first usage in mind.

### Local LLM

When using Ollama:

```text
Repository
    ↓
Local Model
    ↓
Analysis
```

No external LLM API is required.

### GitHub

GitHub authentication is optional and can use an existing local GitHub CLI session.

### Google

Google authentication uses Google's local application-default credential storage for Vertex AI access.

---

# 🛠️ Configuration

DevScope can be configured through environment variables.

```env
# LLM
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434

# Optional GitHub token
GITHUB_TOKEN=

# Optional Google / Gemini configuration
# Configure through:
# devscope auth google --project YOUR_GOOGLE_CLOUD_PROJECT
```

---

# 🎯 Who Is DevScope For?

DevScope is particularly useful when you are:

* Starting a new developer tool
* Researching an AI/ML idea
* Evaluating an open-source concept
* Looking for existing implementations
* Comparing competing architectures
* Finding unexplored technical gaps
* Validating whether an idea is worth building
* Researching before designing an MCP server

---

# 🧪 Project Status

DevScope is an experimental research instrument focused on exploring **AI-assisted software research and repository-level analysis**.

The project is actively evolving, and the research pipeline may change as new analysis strategies and integrations are added.

---

# 🗺️ Roadmap

Potential future directions:

* [ ] Multi-repository architectural comparison
* [ ] Dependency graph analysis
* [ ] Repository health scoring
* [ ] Historical GitHub analysis
* [ ] Issue and PR analysis
* [ ] Semantic code search
* [ ] Automated competitor matrices
* [ ] Research report export
* [ ] Persistent research sessions
* [ ] Multi-agent research workflows
* [ ] Multi-hop repository reasoning
* [ ] Retrieval-backed evidence verification

---

<img width="1272" height="1272" alt="Screenshot 2026-08-27 142715" src="https://github.com/user-attachments/assets/0d24966e-2234-4fd9-97d6-4931cc560beb" />

<img width="1292" height="1184" alt="Screenshot 2026-08-27 142744" src="https://github.com/user-attachments/assets/d9aeaf83-63f8-4e7b-b492-af5991bf383a" />


---

<div align="center">

### **DEV//SCOPE**

**Research the ecosystem. Find the gaps. Build what comes next.**

</div>
