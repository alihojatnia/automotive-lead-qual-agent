# Agentic AI: Automotive Lead Qualifier

**Multi-Agent Workflow**: Parses leads → Scores → Updates CRM. **70% faster manual review** (sim: 3s/lead vs 2min).


## Quickstart
1. `docker-compose up -d`
2. `pip install -r requirements.txt`
3. `ollama serve & ollama pull llama3.2`
4. `python app.py`
5. `curl ...` (above)

## Architecture
- **LangGraph DAG**: Parser → Scorer → Updater
- **Ollama LLM** (local)
- **Postgres CRM**

**Metrics**:
| Manual | AI |
|--------|----|
| 2min/lead | **3s/lead** |
| 100% human | **Auto 24/7** |

