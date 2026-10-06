# Smart Pocket AI – Streamlit demo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501 with generated demo data (no setup needed).

Pages: Dashboard · Add Expense (quick natural-language add) · Insights (budgets, forecast,
anomalies, subscriptions) · Assistant (offline; optional Claude via `ANTHROPIC_API_KEY`) · Data (edit/import/export CSV).
