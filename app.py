import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="🧠 Life-OS Wellbeing Dashboard",
    page_icon="🧠",
    layout="wide"
)

# -----------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)

# -----------------------------
# LOAD DATA
# -----------------------------
try:
    df = pd.read_csv("screentime.csv")
except FileNotFoundError:
    st.error("❌ screentime.csv not found.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])

# -----------------------------
# TITLE
# -----------------------------
st.title("🧠 Life-OS Wellbeing Dashboard")
st.caption("Your AI-powered Digital Wellness Companion")

st.divider()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("⚙ Dashboard Controls")

selected_date = st.sidebar.selectbox(
    "Select Date",
    sorted(df["Date"].dt.date.unique(), reverse=True)
)

daily_goal = st.sidebar.slider(
    "Daily Screen Time Goal (minutes)",
    min_value=60,
    max_value=600,
    value=240,
    step=30
)

# -----------------------------
# FILTER DATA
# -----------------------------
today = df[df["Date"].dt.date == selected_date]

if today.empty:
    st.warning("No data available for selected date.")
    st.stop()

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_minutes = today["Minutes_Used"].sum()

most_used_app = (
    today.groupby("App_Name")["Minutes_Used"]
    .sum()
    .idxmax()
)

goal_difference = total_minutes - daily_goal

category_summary = (
    today.groupby("Category")["Minutes_Used"]
    .sum()
)
# -----------------------------
# KPI ROW
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📱 Total Screen Time",
        value=f"{total_minutes} min"
    )

with col2:
    st.metric(
        label="🔥 Most Used App",
        value=most_used_app
    )

with col3:
    st.metric(
        label="🎯 Goal Difference",
        value=f"{goal_difference} min",
        delta=goal_difference,
        delta_color="inverse"
    )

st.divider()

# -----------------------------
# PROGRESS BAR
# -----------------------------
st.subheader("📊 Goal Progress")

progress = total_minutes / daily_goal

if progress > 1:
    progress = 1.0

st.progress(progress)

if total_minutes <= daily_goal:
    st.success("✅ Great job! You stayed within your daily goal.")
else:
    st.error("⚠️ You exceeded today's screen time goal.")

st.divider()

# -----------------------------
# CHARTS
# -----------------------------
left, right = st.columns(2)

with left:

    st.subheader("📈 14-Day Screen Time Trend")

    daily_usage = (
        df.groupby("Date")["Minutes_Used"]
        .sum()
        .sort_index()
    )

    st.line_chart(daily_usage)

with right:

    st.subheader("📊 Today's Category Usage")

    st.bar_chart(category_summary)

st.divider()

# -----------------------------
# DAILY APP USAGE TABLE
# -----------------------------
st.subheader("📋 Today's App Usage")

display_df = (
    today
    .sort_values("Minutes_Used", ascending=False)
    .reset_index(drop=True)
)

st.dataframe(
    display_df,
    use_container_width=True
)

st.divider()

# -----------------------------
# WEEKLY INSIGHTS
# -----------------------------
st.subheader("📌 Quick Insights")

colA, colB, colC = st.columns(3)

highest_day = (
    df.groupby("Date")["Minutes_Used"]
    .sum()
)

lowest_day = highest_day.idxmin()
highest_day_date = highest_day.idxmax()

average_minutes = round(highest_day.mean())

with colA:
    st.info(f"📉 Lowest Usage\n\n{lowest_day.strftime('%d %b')}")

with colB:
    st.warning(f"📈 Highest Usage\n\n{highest_day_date.strftime('%d %b')}")

with colC:
    st.success(f"📊 Daily Average\n\n{average_minutes} min")

st.divider()

# -----------------------------
# SUMMARY STRING FOR GEMINI
# -----------------------------
summary = (
    today.groupby("Category")["Minutes_Used"]
    .sum()
    .to_string()
)
# -----------------------------
# AI COACH SECTION
# -----------------------------
st.subheader("🤖 Life-OS AI Coach")

prompt = f"""
You are Life-OS, a brutally honest but supportive productivity and lifestyle coach.

Today's screen time summary:

{summary}

Total screen time: {total_minutes} minutes.
Daily goal: {daily_goal} minutes.

Your task:

1. Analyze today's habits.
2. Mention which category consumed the most time.
3. Explain whether the screen time is healthy.
4. Suggest REAL WORLD replacements.

For example:

Instead of Instagram:
- Go for a 30-minute walk.

Instead of YouTube:
- Read 20 pages.

Instead of Netflix:
- Meal prep.

Instead of Gaming:
- Workout.

Instead of scrolling:
- Stretching.

Be motivating but direct.

Maximum 200 words.
"""

if client:

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        advice = response.text

    except Exception as e:

        advice = f"Gemini Error:\n{e}"

else:

    advice = "Gemini API key not found."

if total_minutes > daily_goal:

    st.warning(advice)

else:

    st.info(advice)

st.divider()

# -----------------------------
# GUILT-TRIP AVATAR
# -----------------------------
st.subheader("🎭 Today's Productivity Avatar")

if total_minutes > daily_goal:

    avatar_prompt = (
        "a tired zombie staring at a glowing smartphone, "
        "dark room, messy desk, digital art"
    )

else:

    avatar_prompt = (
        "a focused warrior reading a book in sunlight, "
        "healthy lifestyle, motivational digital art"
    )

avatar_url = (
    "https://image.pollinations.ai/prompt/"
    + avatar_prompt.replace(" ", "%20")
)

st.image(
    avatar_url,
    caption="AI Generated Mood Avatar",
    use_container_width=True
)

st.divider()

# -----------------------------
# DOWNLOAD TODAY'S DATA
# -----------------------------
st.subheader("📥 Export Today's Data")

csv = today.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Today's Report",
    csv,
    file_name="today_screen_time.csv",
    mime="text/csv"
)

st.divider()

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(
    """
---
### 🧠 Life-OS Wellbeing Dashboard

Built with:

- Streamlit
- Pandas
- Google Gemini API
- AI Lifestyle Coaching

Made for **MirAI School of Technology – AI Builder Internship 2026**
"""
)