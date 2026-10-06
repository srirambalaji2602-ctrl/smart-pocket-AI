"""
Smart Pocket AI - runnable Streamlit demo prototype
Run:  streamlit run app.py
"""
import os
import re
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Smart Pocket AI", page_icon="👛", layout="wide")

# ----------------------------------------------------------------------------
# "AI" layer 1: keyword-based auto-categoriser (swap for a real model later)
# ----------------------------------------------------------------------------
CATEGORY_RULES = {
    "Food & Dining": ["coffee", "cafe", "lunch", "dinner", "breakfast", "pizza", "burger",
                      "restaurant", "swiggy", "zomato", "biryani", "snack", "tea"],
    "Groceries": ["grocery", "groceries", "vegetables", "milk", "supermarket", "bigbasket", "fruits"],
    "Transport": ["uber", "ola", "bus", "metro", "fuel", "petrol", "diesel", "auto", "taxi", "train"],
    "Shopping": ["amazon", "flipkart", "shirt", "shoes", "clothes", "mall", "myntra"],
    "Entertainment": ["movie", "netflix", "spotify", "game", "concert", "prime", "hotstar"],
    "Bills & Utilities": ["electricity", "water", "internet", "wifi", "recharge", "rent", "phone bill"],
    "Health": ["pharmacy", "doctor", "medicine", "gym", "hospital", "clinic"],
    "Education": ["course", "book", "books", "tuition", "udemy", "stationery"],
}
CATEGORIES = list(CATEGORY_RULES) + ["Other"]
DEFAULT_BUDGETS = {
    "Food & Dining": 4000, "Groceries": 5000, "Transport": 3000, "Shopping": 4000,
    "Entertainment": 1500, "Bills & Utilities": 6000, "Health": 2000,
    "Education": 2000, "Other": 1500,
}


def categorize(text: str) -> str:
    t = text.lower()
    for cat, words in CATEGORY_RULES.items():
        if any(w in t for w in words):
            return cat
    return "Other"


# ----------------------------------------------------------------------------
# Data helpers
# ----------------------------------------------------------------------------
def make_demo_data(days: int = 75, seed: int = 7) -> pd.DataFrame:
    rng = random.Random(seed)
    samples = [
        ("Morning coffee", 80, 180), ("Lunch at cafe", 150, 400), ("Swiggy dinner", 250, 600),
        ("Uber ride", 120, 450), ("Metro card recharge", 200, 500), ("Vegetables", 150, 500),
        ("Supermarket groceries", 600, 2200), ("Amazon order", 300, 2500), ("Movie tickets", 300, 800),
        ("Pharmacy", 100, 700), ("Online course", 400, 1500), ("Petrol", 500, 1500),
    ]
    rows = []
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        for _ in range(rng.choice([0, 1, 1, 2, 2, 3])):
            desc, lo, hi = rng.choice(samples)
            rows.append((d, desc, round(rng.uniform(lo, hi), 2)))
        # recurring subscriptions / bills
        if d.day == 5:
            rows.append((d, "Netflix subscription", 649.0))
            rows.append((d, "Spotify subscription", 119.0))
        if d.day == 1:
            rows.append((d, "Electricity bill", 1800.0))
            rows.append((d, "Internet wifi", 799.0))
    # one deliberate outlier for anomaly detection
    rows.append((today - timedelta(days=3), "Shoes at mall", 7499.0))
    df = pd.DataFrame(rows, columns=["date", "description", "amount"])
    df["category"] = df["description"].map(categorize)
    return df.sort_values("date").reset_index(drop=True)


def parse_quick_add(text: str):
    """'coffee 150 yesterday' -> (date, 'coffee', 150.0)"""
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if not m:
        return None
    amount = float(m.group(1))
    d = date.today()
    low = text.lower()
    if "yesterday" in low:
        d -= timedelta(days=1)
    elif (dm := re.search(r"(\d+)\s*days?\s*ago", low)):
        d -= timedelta(days=int(dm.group(1)))
    desc = re.sub(r"(\d+(?:\.\d+)?)|yesterday|today|\d+\s*days?\s*ago|[₹$€]|rs\.?", "", text, flags=re.I)
    desc = re.sub(r"\s+", " ", desc).strip().title() or "Expense"
    return d, desc, amount


def this_month(df: pd.DataFrame) -> pd.DataFrame:
    t = date.today()
    return df[(pd.to_datetime(df["date"]).dt.month == t.month) & (pd.to_datetime(df["date"]).dt.year == t.year)]


# ----------------------------------------------------------------------------
# "AI" layer 2: insights
# ----------------------------------------------------------------------------
def month_forecast(df: pd.DataFrame) -> float:
    m = this_month(df)
    today = date.today()
    days_elapsed = max(today.day, 1)
    days_in_month = (pd.Timestamp(today) + pd.offsets.MonthEnd(0)).day
    return m["amount"].sum() / days_elapsed * days_in_month


def find_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for cat, g in df.groupby("category"):
        if len(g) < 5:
            continue
        mu, sd = g["amount"].mean(), g["amount"].std()
        if sd and sd > 0:
            flagged = g[(g["amount"] - mu) / sd > 2.2].copy()
            flagged["typical"] = round(mu, 0)
            out.append(flagged)
    return pd.concat(out) if out else pd.DataFrame(columns=list(df.columns) + ["typical"])


def find_subscriptions(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("description").agg(count=("amount", "size"), avg=("amount", "mean"),
                                       std=("amount", "std"), last=("date", "max")).reset_index()
    g["std"] = g["std"].fillna(0)
    subs = g[(g["count"] >= 2) & (g["std"] < 1) & (g["description"].str.contains(
        "subscription|netflix|spotify|prime|bill|wifi|internet|rent", case=False, regex=True))]
    return subs[["description", "avg", "count", "last"]]


def smart_tips(df: pd.DataFrame, budgets: dict, monthly_budget: float, sym: str) -> list:
    tips = []
    m = this_month(df)
    spent = m.groupby("category")["amount"].sum()
    for cat, amt in spent.items():
        b = budgets.get(cat, 0)
        if b and amt > b:
            tips.append(f"🚨 **{cat}** is over budget by {sym}{amt - b:,.0f}.")
        elif b and amt > 0.8 * b:
            tips.append(f"⚠️ **{cat}** has used {amt / b:.0%} of its budget.")
    fc = month_forecast(df)
    if fc > monthly_budget:
        tips.append(f"📈 At the current pace you'll spend **{sym}{fc:,.0f}** this month, "
                    f"{sym}{fc - monthly_budget:,.0f} above your budget.")
    else:
        tips.append(f"✅ On track: projected month-end spend is **{sym}{fc:,.0f}** "
                    f"(budget {sym}{monthly_budget:,.0f}).")
    food = df[df["category"] == "Food & Dining"]
    if len(food) >= 10:
        tips.append(f"☕ You've logged {len(food)} food & dining purchases. Cooking a few more meals "
                    f"could save roughly {sym}{food['amount'].mean() * 4:,.0f}/month.")
    return tips


# ----------------------------------------------------------------------------
# Assistant (rule-based; uses Claude if ANTHROPIC_API_KEY is set)
# ----------------------------------------------------------------------------
def data_summary(df: pd.DataFrame, sym: str) -> str:
    m = this_month(df)
    by_cat = m.groupby("category")["amount"].sum().round(0).to_dict()
    return (f"Currency: {sym}. This month so far: total {m['amount'].sum():,.0f}; by category: {by_cat}. "
            f"All-time rows: {len(df)}. Forecast month-end: {month_forecast(df):,.0f}.")


def rule_based_answer(q: str, df: pd.DataFrame, budgets: dict, monthly_budget: float, sym: str) -> str:
    ql = q.lower()
    m = this_month(df)
    for cat in CATEGORIES:
        if cat.lower().split(" ")[0] in ql:
            amt = m[m["category"] == cat]["amount"].sum()
            b = budgets.get(cat, 0)
            return f"You've spent **{sym}{amt:,.0f}** on {cat} this month" + \
                   (f" ({amt / b:.0%} of your {sym}{b:,.0f} budget)." if b else ".")
    if any(w in ql for w in ["forecast", "predict", "month end", "month-end", "project"]):
        return f"Projected spend this month: **{sym}{month_forecast(df):,.0f}** vs budget {sym}{monthly_budget:,.0f}."
    if any(w in ql for w in ["biggest", "largest", "highest", "top"]):
        r = df.sort_values("amount", ascending=False).iloc[0]
        return f"Your largest expense is **{r['description']}** at {sym}{r['amount']:,.0f} on {r['date']}."
    if "week" in ql:
        w = df[pd.to_datetime(df["date"]) >= pd.Timestamp(date.today() - timedelta(days=7))]
        return f"Last 7 days: **{sym}{w['amount'].sum():,.0f}** across {len(w)} transactions."
    if "subscription" in ql:
        s = find_subscriptions(df)
        return "Recurring payments detected: " + ", ".join(
            f"{r.description} ({sym}{r.avg:,.0f})" for r in s.itertuples()) if len(s) else "No subscriptions found."
    if "save" in ql or "tip" in ql or "advice" in ql:
        return "\n\n".join(smart_tips(df, budgets, monthly_budget, sym))
    if any(w in ql for w in ["total", "spent", "spend", "how much"]):
        return f"Total this month: **{sym}{m['amount'].sum():,.0f}** ({len(m)} transactions). " \
               f"Budget left: {sym}{monthly_budget - m['amount'].sum():,.0f}."
    return ("I can answer things like *'how much on food?'*, *'forecast this month'*, "
            "*'biggest expense'*, *'last week'*, *'subscriptions'*, or *'give me savings tips'*.")


def ask_assistant(q, df, budgets, monthly_budget, sym):
    key = os.getenv("ANTHROPIC_API_KEY") or st.session_state.get("api_key")
    if key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            msg = client.messages.create(
                model="claude-sonnet-4-6", max_tokens=400,
                system="You are Smart Pocket AI, a concise, friendly personal-finance assistant. "
                       "Answer using only the data summary provided. " + data_summary(df, sym),
                messages=[{"role": "user", "content": q}],
            )
            return msg.content[0].text
        except Exception as e:  # fall back gracefully
            return rule_based_answer(q, df, budgets, monthly_budget, sym) + f"\n\n_(LLM unavailable: {e})_"
    return rule_based_answer(q, df, budgets, monthly_budget, sym)


# ----------------------------------------------------------------------------
# State & sidebar
# ----------------------------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = make_demo_data()
if "chat" not in st.session_state:
    st.session_state.chat = [("assistant", "Hi! I'm your Smart Pocket AI 👛. Ask me about your spending.")]
if "budgets" not in st.session_state:
    st.session_state.budgets = DEFAULT_BUDGETS.copy()

with st.sidebar:
    st.title("👛 Smart Pocket AI")
    page = st.radio("Navigate", ["Dashboard", "Add Expense", "Insights", "Assistant", "Data"], label_visibility="collapsed")
    st.divider()
    sym = st.selectbox("Currency", ["₹", "$", "€", "£"])
    monthly_budget = st.number_input("Monthly budget", min_value=1000, value=int(sum(DEFAULT_BUDGETS.values())), step=500)
    with st.expander("Category budgets"):
        for c in CATEGORIES:
            st.session_state.budgets[c] = st.number_input(c, 0, 100000, st.session_state.budgets[c], 100, key=f"b_{c}")
    with st.expander("Optional: Claude API key"):
        st.text_input("ANTHROPIC_API_KEY", type="password", key="api_key",
                      help="Leave empty to use the built-in offline assistant.")
    if st.button("🔄 Reset demo data", use_container_width=True):
        st.session_state.df = make_demo_data(seed=random.randint(1, 999))
        st.rerun()

df = st.session_state.df
budgets = st.session_state.budgets
m = this_month(df)

# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
if page == "Dashboard":
    st.header("Dashboard")
    spent = m["amount"].sum()
    left = monthly_budget - spent
    days = max(date.today().day, 1)
    top_cat = m.groupby("category")["amount"].sum().idxmax() if len(m) else "-"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Spent this month", f"{sym}{spent:,.0f}")
    c2.metric("Budget left", f"{sym}{left:,.0f}", delta=f"{left / monthly_budget:.0%} remaining")
    c3.metric("Avg / day", f"{sym}{spent / days:,.0f}")
    c4.metric("Top category", top_cat)

    st.progress(min(spent / monthly_budget, 1.0), text=f"{spent / monthly_budget:.0%} of monthly budget used")

    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("Spending by category")
        if len(m):
            st.bar_chart(m.groupby("category")["amount"].sum().sort_values(ascending=False))
        else:
            st.info("No expenses this month yet.")
    with right_col:
        st.subheader("Cumulative spend (this month)")
        if len(m):
            daily = m.groupby("date")["amount"].sum().cumsum()
            st.line_chart(daily)

    st.subheader("Recent transactions")
    st.dataframe(df.sort_values("date", ascending=False).head(10), use_container_width=True, hide_index=True)

elif page == "Add Expense":
    st.header("Add Expense")
    st.subheader("⚡ Quick add (natural language)")
    q = st.text_input("Try: `coffee 150 yesterday` or `uber 320 2 days ago`")
    if st.button("Add quickly") and q:
        parsed = parse_quick_add(q)
        if parsed:
            d, desc, amt = parsed
            cat = categorize(desc)
            st.session_state.df = pd.concat(
                [df, pd.DataFrame([(d, desc, amt, cat)], columns=df.columns)], ignore_index=True)
            st.success(f"Added **{desc}** {sym}{amt:,.0f} on {d} → auto-categorised as **{cat}**")
        else:
            st.error("Couldn't find an amount in that text.")

    st.divider()
    st.subheader("Manual entry")
    with st.form("manual"):
        a, b, c = st.columns([2, 1, 1])
        desc = a.text_input("Description")
        amt = b.number_input("Amount", min_value=0.0, step=10.0)
        d = c.date_input("Date", date.today())
        suggestion = categorize(desc) if desc else "Other"
        cat = st.selectbox("Category (AI suggestion preselected)", CATEGORIES, index=CATEGORIES.index(suggestion))
        if st.form_submit_button("Save expense") and desc and amt > 0:
            st.session_state.df = pd.concat(
                [df, pd.DataFrame([(d, desc, amt, cat)], columns=df.columns)], ignore_index=True)
            st.success("Saved! Check the Dashboard.")

elif page == "Insights":
    st.header("AI Insights")
    for t in smart_tips(df, budgets, monthly_budget, sym):
        st.markdown(f"- {t}")

    st.subheader("Category budgets")
    spent_by = m.groupby("category")["amount"].sum()
    for cat in CATEGORIES:
        s, b = spent_by.get(cat, 0.0), budgets.get(cat, 1)
        st.progress(min(s / b, 1.0) if b else 0.0, text=f"{cat}: {sym}{s:,.0f} / {sym}{b:,.0f}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔍 Unusual purchases")
        an = find_anomalies(df)
        if len(an):
            st.dataframe(an[["date", "description", "amount", "typical"]], hide_index=True, use_container_width=True)
        else:
            st.success("Nothing unusual detected.")
    with c2:
        st.subheader("🔁 Recurring payments")
        subs = find_subscriptions(df)
        st.dataframe(subs, hide_index=True, use_container_width=True) if len(subs) else st.info("None detected.")

    st.subheader("Weekly trend")
    wk = df.assign(week=pd.to_datetime(df["date"]).dt.to_period("W").astype(str)).groupby("week")["amount"].sum()
    st.area_chart(wk)

elif page == "Assistant":
    st.header("Ask Pocket AI")
    st.caption("Offline rule-based assistant by default; add a Claude API key in the sidebar for open-ended answers.")
    for role, text in st.session_state.chat:
        st.chat_message(role).markdown(text)
    prompt = st.chat_input("e.g. How much did I spend on food?")
    if prompt:
        st.session_state.chat.append(("user", prompt))
        st.session_state.chat.append(("assistant", ask_assistant(prompt, df, budgets, monthly_budget, sym)))
        st.rerun()

elif page == "Data":
    st.header("Data")
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state.df = edited
    st.download_button("⬇️ Export CSV", edited.to_csv(index=False), "pocket_expenses.csv", "text/csv")
    up = st.file_uploader("Import CSV (columns: date, description, amount[, category])", type="csv")
    if up:
        new = pd.read_csv(up)
        new["date"] = pd.to_datetime(new["date"]).dt.date
        if "category" not in new:
            new["category"] = new["description"].map(categorize)
        st.session_state.df = new[["date", "description", "amount", "category"]]
        st.success(f"Imported {len(new)} rows.")
