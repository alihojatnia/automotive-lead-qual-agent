**COPY-PASTE THIS ENTIRE README → `README.md`**

```markdown
# AI Automotive Lead Qualifier  
**Score leads in seconds. No more guesswork.**

---

## What It Does

You type a customer message like:

> *"Hi, electric SUV under €40k, family of 4, ASAP! John – john@test.com"*

And **in 1 second**, it tells you:

```
Score: 9.0/10  
Action: Schedule test drive for Tesla Model Y  
Lead ID: 5
```

It **parses**, **scores**, **saves to DB**, and **shows results live** in a clean web UI.

---

## Features

| Feature | Status |
|--------|--------|
| Parse messy customer messages | Yes |
| Score leads 0–10 with AI | Yes |
| Suggest next action (test drive, email, etc.) | Yes |
| Save to PostgreSQL | Yes |
| Live web dashboard | Yes |
| Zero crashes (even if AI fails) | Yes |

---


## How to Run (3 Steps)

### 1. Clone & Enter
```bash
git clone https://github.com/yourusername/automotive-lead-qual-agent.git
cd automotive-lead-qual-agent
```

### 2. Install & Start
```bash
pip install -r requirements.txt
ollama pull llama3.2:1b        # ← Smarter AI recommended
python app.py
```

### 3. Open in Browser
```bash
open http://localhost:5000
```

Paste a message → click **Qualify Lead** → **boom!**

---

### Tech Stack

- **Flask** – Web server
- **LangGraph** – AI agent workflow
- **Ollama** – Runs `llama3.2:3b` locally
- **PostgreSQL** – Stores leads
- **HTML + JS** – Live UI 

---

### Project Structure

```
.
├── app.py          ← Web server + UI
├── agents.py       ← AI brain (parsing + scoring)
├── database.py     ← DB setup
├── models.py       ← Lead model
├── requirements.txt
└── README.md       
```

---

### Example Outputs

| Message | Score | Action |
|--------|-------|--------|
| `electric SUV under €40k, ASAP` | 9.0 | Schedule test drive |
| `maybe a sedan next year` | 3.5 | Send brochure |
| `just browsing` | 1.0 | Nurture email |

---



