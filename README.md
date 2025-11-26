# LLM Quiz Solver

Automated quiz solving system using LLMs for data analysis tasks.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```
ANTHROPIC_API_KEY=your_key
STUDENT_EMAIL=your_email
STUDENT_SECRET=your_secret
```

3. Run:
```bash
python app.py
```

## API Endpoint

POST `/quiz` - Receives and solves quiz tasks

## License

MIT
