import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import os

# Supabase connection
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials missing. Add them to Modal secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load dataset
response = supabase.table("websites").select("*").execute()

if not response.data:
    st.warning("No data found in Supabase table 'websites'.")
    st.stop()

df = pd.DataFrame(response.data)

# Convert timestamps
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Dashboard Heade
st.title("OCC Overview")
st.write(
    "This dashboard analyzes fraud trends, keyword behavior, clustering, "
    "and text insight stored in Supabase."
)

# Fraud Trends SECTION
st.header("Fraud Trends")

# Trend 1: Fraud case counts per day
if "date" in df.columns:
    df_counts = (
        df.groupby(df["date"].dt.date)
        .size()
        .reset_index(name="fraud_count")
    )

    fig_trend = px.line(
        df_counts,
        x="date",
        y="fraud_count",
        markers=True,
        title="Number of Fraud Reports Over Time"
    )
    st.plotly_chart(fig_trend)

# Trend 2: Average Fraud Score per day
if "fraud_score" in df.columns and "date" in df.columns:
    df_score = (
        df.groupby(df["date"].dt.date)["fraud_score"]
        .mean()
        .reset_index(name="avg_fraud_score")
    )

    fig_score = px.line(
        df_score,
        x="date",
        y="avg_fraud_score",
        markers=True,
        title="Average Fraud Score Over Time"
    )
    st.plotly_chart(fig_score)

# KEYWORD / CLUSTER CHART
if "kmeans_cluster" in df.columns:
    fig_cluster = px.histogram(
        df,
        x="kmeans_cluster",
        title="Frequency of K-Means Fraud Clusters"
    )
    st.plotly_chart(fig_cluster)

# Search Library
st.header("Search Library")

search_query = st.text_input("Search cleaned_text or fraud_reason:")

if search_query:
    results = df[
        df["cleaned_text"].str.contains(search_query, case=False, na=False) |
        df["fraud_reason"].str.contains(search_query, case=False, na=False)
    ]

    st.write(f"### {len(results)} results found")

    for _, row in results.iterrows():
        with st.expander(row.get("type", "Fraud Entry")):
            st.write("**Link:**", row.get("link"))
            st.write("**Fraud Reason:**")
            st.write(row.get("fraud_reason"))
            st.write("**Fraud Score:**", row.get("fraud_score"))
            st.write("**Confidence:**", row.get("fraud_confidence"))
            st.write("**Cluster:**", row.get("kmeans_cluster"))
            st.write("**Text Extract:**")
            st.write(row.get("cleaned_text"))

else:
    st.info("Enter a search term to explore your fraud dataset.")

import plotly.express as px

# Full table from supabase
st.subheader("Full Dataset")
st.dataframe(df)
