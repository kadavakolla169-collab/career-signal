import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_connection

st.set_page_config(
    page_title="Career Signal",
    page_icon="📊",
    layout="wide"
)

st.sidebar.title("Career Signal")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Market Overview", "Skills by Role", "Cloud Platforms", "Experience & Salary"]
)

if page == "Market Overview":
    st.title("Job Market Overview")
    st.markdown("Real-time intelligence from 55+ data job postings")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jobs Analyzed", "55")
    col2.metric("Unique Skills", "50+")
    col3.metric("Roles Covered", "3")
    col4.metric("Companies", "40+")
    
    st.markdown("---")
    
    conn = get_connection()
    df = pd.read_sql("""
        SELECT skill, COUNT(*) as demand_count
        FROM (
            SELECT json_array_elements_text(technical_skills::json) as skill
            FROM job_skills
        ) skills
        GROUP BY skill
        ORDER BY demand_count DESC
        LIMIT 15
    """, conn)
    conn.close()
    
    fig = px.bar(
        df,
        x="demand_count",
        y="skill",
        orientation="h",
        title="Top 15 Most In-Demand Skills",
        color="demand_count",
        color_continuous_scale="blues",
        labels={"demand_count": "Number of Jobs", "skill": "Skill"}
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

elif page == "Skills by Role":
    st.title("Skills by Role")
    st.markdown("Compare skill requirements across different data roles")
    
    role = st.selectbox("Select Role", ["data engineer", "data scientist", "data analyst"])
    
    conn = get_connection()
    df_role = pd.read_sql("""
        SELECT skill, COUNT(*) as demand_count
        FROM (
            SELECT js.job_id, j.role, json_array_elements_text(js.technical_skills::json) as skill
            FROM job_skills js
            JOIN jobs j ON js.job_id = j.job_id
            WHERE j.role = %(role)s
        ) skills
        GROUP BY skill
        ORDER BY demand_count DESC
        LIMIT 10
    """, conn, params={"role": role})
    conn.close()
    
    fig = px.bar(
        df_role,
        x="demand_count",
        y="skill",
        orientation="h",
        title=f"Top Skills for {role.title()}",
        color="demand_count",
        color_continuous_scale="teal",
        labels={"demand_count": "Number of Jobs", "skill": "Skill"}
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

elif page == "Cloud Platforms":
    st.title("Cloud Platform Demand")
    st.markdown("Which cloud platforms are employers looking for?")
    
    conn = get_connection()
    df_cloud = pd.read_sql("""
        SELECT platform, COUNT(*) as demand_count
        FROM (
            SELECT json_array_elements_text(cloud_platforms::json) as platform
            FROM job_skills
            WHERE cloud_platforms != '[]'
        ) platforms
        GROUP BY platform
        ORDER BY demand_count DESC
    """, conn)
    conn.close()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            df_cloud,
            x="platform",
            y="demand_count",
            title="Cloud Platform Demand",
            color="demand_count",
            color_continuous_scale="oranges",
            labels={"demand_count": "Number of Jobs", "platform": "Platform"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig2 = px.pie(
            df_cloud,
            values="demand_count",
            names="platform",
            title="Cloud Platform Market Share"
        )
        st.plotly_chart(fig2, use_container_width=True)

elif page == "Experience & Salary":
    st.title("Experience & Visa Insights")
    st.markdown("What experience level does the market demand?")
    
    conn = get_connection()
    df_exp = pd.read_sql("""
        SELECT j.role, js.experience_level, COUNT(*) as count
        FROM job_skills js
        JOIN jobs j ON js.job_id = j.job_id
        WHERE js.experience_level IS NOT NULL
        GROUP BY j.role, js.experience_level
        ORDER BY j.role, count DESC
    """, conn)
    conn.close()
    
    fig = px.bar(
        df_exp,
        x="role",
        y="count",
        color="experience_level",
        title="Experience Level Distribution by Role",
        barmode="group",
        labels={"count": "Number of Jobs", "role": "Role", "experience_level": "Level"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    conn = get_connection()
    df_visa = pd.read_sql("""
        SELECT 
            CASE WHEN visa_sponsorship = true THEN 'Yes' 
                 WHEN visa_sponsorship = false THEN 'No'
            END as sponsorship,
            COUNT(*) as count
        FROM job_skills
        WHERE visa_sponsorship IS NOT NULL
        GROUP BY visa_sponsorship
    """, conn)
    conn.close()
    
    fig2 = px.pie(
        df_visa,
        values="count",
        names="sponsorship",
        title="Visa Sponsorship Availability",
        color_discrete_map={"Yes": "green", "No": "red"}
    )
    st.plotly_chart(fig2, use_container_width=True)