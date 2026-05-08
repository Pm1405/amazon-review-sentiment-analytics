import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

st.set_page_config(page_title="Amazon Review Analytics", layout="wide")
st.title("🛒 Amazon Review Insights")
st.caption("Understanding what customers really feel about products — powered by AI sentiment analysis")

session = get_active_session()

@st.cache_data
def load_sentiment_summary():
    return session.sql("""
        SELECT AI_SENTIMENT_LABEL, COUNT(*) AS COUNT
        FROM REVIEW_ANALYTICS.RAW.REVIEWS_WITH_SENTIMENT
        GROUP BY AI_SENTIMENT_LABEL
    """).to_pandas()

@st.cache_data
def load_department_stats():
    return session.sql("""
        SELECT MAINDEPARTMENT AS DEPARTMENT, 
            COUNT(*) AS TOTAL_REVIEWS,
            ROUND(AVG(TRY_CAST(REVIEWSTAR AS FLOAT)), 1) AS AVG_RATING,
            ROUND(AVG(AI_SENTIMENT_SCORE) * 100, 1) AS HAPPINESS_SCORE,
            SUM(CASE WHEN AI_SENTIMENT_LABEL = 'Positive' THEN 1 ELSE 0 END) AS HAPPY_REVIEWS,
            SUM(CASE WHEN AI_SENTIMENT_LABEL = 'Negative' THEN 1 ELSE 0 END) AS UNHAPPY_REVIEWS,
            SUM(CASE WHEN AI_SENTIMENT_LABEL = 'Neutral' THEN 1 ELSE 0 END) AS MIXED_REVIEWS
        FROM REVIEW_ANALYTICS.RAW.REVIEWS_WITH_SENTIMENT
        WHERE TRY_CAST(REVIEWSTAR AS FLOAT) IS NOT NULL
        GROUP BY MAINDEPARTMENT
        ORDER BY TOTAL_REVIEWS DESC
    """).to_pandas()

@st.cache_data
def load_subdepartment_stats():
    return session.sql("""
        SELECT MAINDEPARTMENT AS DEPARTMENT, SUBDEPARTMENT AS CATEGORY, 
            COUNT(*) AS TOTAL_REVIEWS,
            ROUND(AVG(TRY_CAST(REVIEWSTAR AS FLOAT)), 1) AS AVG_RATING,
            ROUND(AVG(AI_SENTIMENT_SCORE) * 100, 1) AS HAPPINESS_SCORE
        FROM REVIEW_ANALYTICS.RAW.REVIEWS_WITH_SENTIMENT
        WHERE TRY_CAST(REVIEWSTAR AS FLOAT) IS NOT NULL
        GROUP BY MAINDEPARTMENT, SUBDEPARTMENT
        ORDER BY HAPPINESS_SCORE DESC
    """).to_pandas()

@st.cache_data
def load_mismatches():
    return session.sql("""
        SELECT MAINDEPARTMENT AS DEPARTMENT, PRODUCTNAME AS PRODUCT, 
            REVIEWTITLE AS TITLE,
            TRY_CAST(REVIEWSTAR AS FLOAT) AS STARS_GIVEN,
            AI_SENTIMENT_LABEL AS AI_DETECTED_MOOD,
            ROUND(AI_SENTIMENT_SCORE, 3) AS MOOD_SCORE,
            REVIEWTEXT AS REVIEW,
            CASE 
                WHEN TRY_CAST(REVIEWSTAR AS FLOAT) >= 4 AND AI_SENTIMENT_LABEL = 'Negative' 
                    THEN 'Gave high stars but wrote a negative review'
                WHEN TRY_CAST(REVIEWSTAR AS FLOAT) <= 2 AND AI_SENTIMENT_LABEL = 'Positive' 
                    THEN 'Gave low stars but wrote a positive review'
            END AS WHATS_CONFUSING
        FROM REVIEW_ANALYTICS.RAW.REVIEWS_WITH_SENTIMENT
        WHERE TRY_CAST(REVIEWSTAR AS FLOAT) IS NOT NULL
          AND ((TRY_CAST(REVIEWSTAR AS FLOAT) >= 4 AND AI_SENTIMENT_LABEL = 'Negative')
            OR (TRY_CAST(REVIEWSTAR AS FLOAT) <= 2 AND AI_SENTIMENT_LABEL = 'Positive'))
        LIMIT 200
    """).to_pandas()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🏢 By Department", "📂 By Category", "🔍 Suspicious Reviews", "📈 Trends Over Time"])

with tab1:
    st.subheader("How do customers feel overall?")
    st.info("We used AI to read every review and detect whether the customer was **happy**, **unhappy**, or **somewhere in between** — regardless of the star rating they gave.")
    
    sentiment_df = load_sentiment_summary()
    col1, col2, col3 = st.columns(3)
    with col1:
        pos = sentiment_df[sentiment_df["AI_SENTIMENT_LABEL"] == "Positive"]["COUNT"].values
        st.metric("😊 Happy Reviews", f"{pos[0]:,}" if len(pos) > 0 else "0")
    with col2:
        neg = sentiment_df[sentiment_df["AI_SENTIMENT_LABEL"] == "Negative"]["COUNT"].values
        st.metric("😞 Unhappy Reviews", f"{neg[0]:,}" if len(neg) > 0 else "0")
    with col3:
        neu = sentiment_df[sentiment_df["AI_SENTIMENT_LABEL"] == "Neutral"]["COUNT"].values
        st.metric("😐 Mixed/Neutral Reviews", f"{neu[0]:,}" if len(neu) > 0 else "0")

    st.divider()
    st.subheader("Sentiment Breakdown")
    chart_df = sentiment_df.copy()
    chart_df.columns = ["Customer Mood", "Number of Reviews"]
    st.bar_chart(chart_df.set_index("Customer Mood"), color="#4CAF50")

with tab2:
    st.subheader("Which departments make customers happiest?")
    st.info("""
    **Happiness Score** = How positive the review text is on a scale from -100 (very unhappy) to +100 (very happy).  
    **Avg Rating** = The star rating customers gave (1-5 stars).  
    Sometimes these don't match — a customer might give 4 stars but write a frustrated review!
    """)
    
    dept_df = load_department_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Reviews per Department")
        st.bar_chart(dept_df.set_index("DEPARTMENT")["TOTAL_REVIEWS"], color="#2196F3")
    with col2:
        st.subheader("Happiness Score by Department")
        st.bar_chart(dept_df.set_index("DEPARTMENT")["HAPPINESS_SCORE"], color="#FF9800")
    
    st.divider()
    st.subheader("Happy vs Unhappy Reviews by Department")
    mood_df = dept_df.set_index("DEPARTMENT")[["HAPPY_REVIEWS", "UNHAPPY_REVIEWS", "MIXED_REVIEWS"]]
    st.bar_chart(mood_df)
    
    st.divider()
    st.subheader("Full Department Data")
    st.dataframe(dept_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Drill down into product categories")
    st.info("Select a department to see which specific product categories have the happiest (or unhappiest) customers.")
    
    subdept_df = load_subdepartment_stats()
    selected_dept = st.selectbox("Choose a Department:", ["All Departments"] + list(subdept_df["DEPARTMENT"].unique()))
    
    if selected_dept != "All Departments":
        filtered = subdept_df[subdept_df["DEPARTMENT"] == selected_dept]
    else:
        filtered = subdept_df
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Happiness Score by Category")
        chart_data = filtered.set_index("CATEGORY")["HAPPINESS_SCORE"].sort_values()
        st.bar_chart(chart_data, color="#9C27B0")
    with col2:
        st.subheader("Average Star Rating by Category")
        chart_data2 = filtered.set_index("CATEGORY")["AVG_RATING"].sort_values()
        st.bar_chart(chart_data2, color="#F44336")
    
    st.divider()
    st.dataframe(filtered, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("🔍 Reviews that don't add up")
    st.warning("""
    **What is this page?**  
    
    Sometimes customers give **high stars (4-5)** but write **negative/frustrated text**, 
    or give **low stars (1-2)** but write **positive/happy text**.  
    
    These are **suspicious or inconsistent reviews** — the star rating doesn't match what 
    the customer actually wrote. This could mean:
    - The customer accidentally selected the wrong star rating
    - The review is fake or incentivized  
    - The customer had mixed feelings (liked some aspects, hated others)
    
    The AI reads the actual review text and flags these mismatches.
    """)
    
    mismatch_df = load_mismatches()
    
    col1, col2 = st.columns(2)
    with col1:
        high_star_neg = len(mismatch_df[mismatch_df["WHATS_CONFUSING"] == "Gave high stars but wrote a negative review"])
        st.metric("⚠️ High stars + Negative text", high_star_neg)
    with col2:
        low_star_pos = len(mismatch_df[mismatch_df["WHATS_CONFUSING"] == "Gave low stars but wrote a positive review"])
        st.metric("🤔 Low stars + Positive text", low_star_pos)
    
    st.divider()
    filter_type = st.radio("Show me:", ["All mismatches", "High stars but negative text", "Low stars but positive text"], horizontal=True)
    
    if filter_type == "High stars but negative text":
        display_df = mismatch_df[mismatch_df["WHATS_CONFUSING"] == "Gave high stars but wrote a negative review"]
    elif filter_type == "Low stars but positive text":
        display_df = mismatch_df[mismatch_df["WHATS_CONFUSING"] == "Gave low stars but wrote a positive review"]
    else:
        display_df = mismatch_df
    
    st.dataframe(display_df[["PRODUCT", "STARS_GIVEN", "AI_DETECTED_MOOD", "WHATS_CONFUSING", "REVIEW"]], 
                 use_container_width=True, hide_index=True)

with tab5:
    st.subheader("How has customer sentiment changed over time?")
    st.info("This chart shows monthly review volume and sentiment trends. Look for seasonal patterns or shifts in customer satisfaction.")
    
    trend_df = session.sql("""
        SELECT REVIEW_MONTH, DEPARTMENT,
            SUM(TOTAL_REVIEWS) AS REVIEWS,
            ROUND(AVG(AVG_SENTIMENT_SCORE) * 100, 1) AS HAPPINESS_SCORE,
            SUM(POSITIVE_REVIEWS) AS POSITIVE,
            SUM(NEGATIVE_REVIEWS) AS NEGATIVE
        FROM REVIEW_ANALYTICS.ANALYTICS.MART_MONTHLY_TRENDS
        WHERE REVIEW_MONTH >= '2019-01-01'
        GROUP BY REVIEW_MONTH, DEPARTMENT
        ORDER BY REVIEW_MONTH
    """).to_pandas()
    
    selected = st.selectbox("Department:", ["All"] + list(trend_df["DEPARTMENT"].unique()), key="trend_dept")
    if selected != "All":
        trend_df = trend_df[trend_df["DEPARTMENT"] == selected]
    
    monthly = trend_df.groupby("REVIEW_MONTH").agg({"REVIEWS": "sum", "HAPPINESS_SCORE": "mean", "POSITIVE": "sum", "NEGATIVE": "sum"}).reset_index()
    
    st.subheader("Monthly Review Volume")
    st.line_chart(monthly.set_index("REVIEW_MONTH")["REVIEWS"])
    
    st.subheader("Monthly Happiness Score")
    st.line_chart(monthly.set_index("REVIEW_MONTH")["HAPPINESS_SCORE"])
    
    st.subheader("Positive vs Negative Reviews Over Time")
    st.line_chart(monthly.set_index("REVIEW_MONTH")[["POSITIVE", "NEGATIVE"]])
