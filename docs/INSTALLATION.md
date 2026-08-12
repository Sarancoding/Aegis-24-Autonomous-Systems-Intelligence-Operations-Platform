# Aegis-24 Installation Guide

## Prerequisites

Before installing Aegis-24, ensure you have:

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Docker (optional, for containerized deployment)

## Step 1: Clone the Repository

```bash
git clone https://github.com/{ORG_OR_USER}/aegis24-platform.git
cd aegis24-platform
```

## Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

```bash
cp harness/.env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key for LLM access
- `GUARDRAILS_CONFIG` - Path to guardrails configuration
- `PHOENIX_ENDPOINT` - Arize Phoenix endpoint (optional)
- `LANGSMITH_API_KEY` - LangSmith API key (optional)
- `E2B_API_KEY` - E2B sandbox API key (optional)
- `DATABASE_URL` - PostgreSQL connection string (optional)

## Step 5: Initialize Database

```bash
mkdir -p db
python -c "from core.research_graph import SQLiteCheckpointer; SQLiteCheckpointer()"
```

## Step 6: Verify Installation

```bash
python -c "from core.safety_gateway import SafetyGateway; print('Installation successful!')"
```

## Step 7: Run Tests (Optional)

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Ensure virtual environment is activated
   - Re-run `pip install -r requirements.txt`

2. **Database errors**
   - Ensure `db/` directory exists
   - Check file permissions

3. **API key errors**
   - Verify `.env` file is properly configured
   - Check API key validity

## Next Steps

After installation:
1. Review [SETUP.md](SETUP.md) for detailed configuration
2. Read [WORKFLOW.md](WORKFLOW.md) to understand system architecture
3. Run `make run-redteam` to verify security setup
