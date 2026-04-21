import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_connection

st.title("Career Signal")
st.write("Real-time job market intelligence for data professionals")

col1, col2, col3 = st.columns(3)
col1.metric("Total Jobs Analyzed", 55)
col2.metric("Skills Tracked", "50+")
col3.metric("Roles Covered", 3)

st.header("Top In-Demand Skills Overall")
conn = get_connection()
df = pd.read_sql("""
    SELECT skill, COUNT(*) as demand_count
    FROM (
        SELECT json_array_elements_text(technical_skills::json) as skill
        FROM job_skills
    ) skills
    GROUP BY skill
    ORDER BY demand_count DESC
    LIMIT 10
""", conn)
conn.close()
st.bar_chart(df.set_index("skill")["demand_count"])

st.header("Skills by Role")
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
st.bar_chart(df_role.set_index("skill")["demand_count"])

st.header("Cloud Platform Demand")
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
st.bar_chart(df_cloud.set_index("platform")["demand_count"])

st.header("Experience Level Distribution")
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
st.dataframe(df_exp)