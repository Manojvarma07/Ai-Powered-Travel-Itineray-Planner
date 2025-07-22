import streamlit as st
from typing import Dict
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# —————— Load LLM ——————
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile"
)

# —————— Base Cost Data ——————
BASE_COST = {
    "Budget":    {"Hotel": 30,  "Food": 10, "Transport": 5,  "Attractions": 10, "Misc": 5},
    "Mid-Range": {"Hotel": 80,  "Food": 25, "Transport": 15, "Attractions": 25, "Misc": 15},
    "Luxury":    {"Hotel": 200, "Food": 50, "Transport": 50, "Attractions": 50, "Misc": 50},
}

# —————— Region Multipliers ——————
REGION_MULTIPLIER = {
    "Southeast Asia": 0.7,
    "Western Europe": 1.1,
    "North America":  1.3,
    "Eastern Europe": 0.9,
    "South Asia":     0.6,
}

SEASON_MULTIPLIER = {
    "low":  0.8,
    "mid":  1.0,
    "high": 1.3,
}

def get_season(month: int) -> str:
    if month in (1, 2, 11):
        return "low"
    if month in (6, 7, 8, 12):
        return "high"
    return "mid"

def calculate_daily_cost(tier: str, region: str, month: int) -> float:
    base = sum(BASE_COST[tier].values())
    region_factor = REGION_MULTIPLIER.get(region, 1.0)
    season = get_season(month)
    season_factor = SEASON_MULTIPLIER[season]
    return base * region_factor * season_factor

def calculate_budget(days: int, tier: str, region: str) -> float:
    today = datetime.today()
    month = today.month
    daily = calculate_daily_cost(tier, region, month)
    return round(daily * days, 2)

# —————— Prompt Template ——————
itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a futuristic AI travel assistant. Create a {days}-day itinerary for {city} "
     "based on {interests} with a {budget} budget in {region}. "
     "Provide a concise, futuristic-styled itinerary."
    ),
    ("human", "Plan my trip")
])

def travel_planner(city: str, interests: str, days: int, tier: str, region: str) -> str:
    total_cost = calculate_budget(days, tier, region)
    msgs = itinerary_prompt.format_messages(
        city=city,
        interests=interests,
        days=days,
        budget=tier,
        region=region
    )
    response = llm.invoke(msgs)
    content = getattr(response, "content", str(response))
    return f"""
    <div class='itinerary-box'>
      <h2>📍 {city} ({region})</h2>
      <h3>📆 {days} Days | 💰 Estimated Cost: ${total_cost}</h3>
      <div class='itinerary-text'>{content}</div>
    </div>
    """

# —————— Streamlit UI ——————
st.set_page_config(page_title="🚀 AI Travel Planner", page_icon="🌍", layout="wide")

# —————— Futuristic CSS ——————
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #f1f1f1;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton button {
        background: linear-gradient(135deg, #ff7eb3, #ff758c);
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s ease-in-out;
        animation: pulse 1.5s infinite;
    }
    .stButton button:hover {
        transform: scale(1.1);
        box-shadow: 0px 0px 20px #ff758c;
    }
    @keyframes pulse {
        0% { box-shadow: 0px 0px 5px #ff758c; }
        50% { box-shadow: 0px 0px 15px #ff758c; }
        100% { box-shadow: 0px 0px 5px #ff758c; }
    }
    .glowing-title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        text-shadow: 0px 0px 10px #ff7eb3;
        animation: glow 1.5s infinite alternate;
    }
    @keyframes glow {
        0% {text-shadow: 0 0 5px #fff, 0 0 10px #ff7eb3, 0 0 15px #ff758c;}
        100% {text-shadow: 0 0 10px #fff, 0 0 20px #ff7eb3, 0 0 30px #ff758c;}
    }
    .itinerary-box {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0px 0px 15px #ff758c;
        margin: 20px 0;
    }
    .itinerary-text {
        font-size: 18px;
        color: #fff;
        padding: 10px;
        line-height: 1.5;
    }
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid #ff7eb3;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        color: #fff;
        text-shadow: 0px 0px 10px #ff7eb3;
        animation: glowInput 1.5s infinite alternate;
    }
    @keyframes glowInput {
        0% { box-shadow: 0px 0px 5px #ff7eb3; }
        100% { box-shadow: 0px 0px 15px #ff758c; }
    }
    </style>
""", unsafe_allow_html=True)

# —————— App Title & Banner ——————
st.markdown('<p class="glowing-title">🌍 Alpha GenAI Travel Planner</p>', unsafe_allow_html=True)

# —————— Use Relative Path for Image ——————
img_path = os.path.join(os.getcwd(), "An_ultra-futuristic_AI-powered_travel_planner_inte.png")
st.image(img_path, use_container_width=True, caption="🔮 Welcome to the Future of Travel Planning!")

# —————— User Inputs ——————
st.markdown("## 🎯 Select Your Travel Preferences")
col1, col2 = st.columns([1, 1])
with col1:
    city      = st.text_input("🏙️ Destination", placeholder="Enter a city (e.g., Paris)", key="glow_dest")
    interests = st.text_input("🎨 Interests", placeholder="E.g., Museums, Food, Beaches", key="glow_interests")
with col2:
    days   = st.slider("📆 Duration (Days)", 1, 14, 5)
    tier   = st.radio("💰 Budget Category", ["Budget", "Mid-Range", "Luxury"], index=1, horizontal=True)
    region = st.selectbox("🌐 Region", list(REGION_MULTIPLIER.keys()))

st.markdown("---")

# —————— Generate Button & Itinerary ——————
if st.button("🚀 Generate Itinerary"):
    with st.spinner("🔮 Generating your futuristic itinerary..."):
        html = travel_planner(city, interests, days, tier, region)
    st.success("✅ Itinerary Ready!")
    st.markdown(html, unsafe_allow_html=True)

st.markdown("---")
st.markdown("👾 **Powered by AI | Designed for the Future!**")
