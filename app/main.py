import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import PyPDF2
import io
import json

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
    ["Market Overview", "Skills by Role", "Cloud Platforms", "Experience & Salary", "Resume Analysis"]
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

elif page == "Resume Analysis":
    st.title("Resume Analysis")
    st.markdown("Upload your resume and get personalized insights")
    
    target_role = st.selectbox(
        "What role are you targeting?",
        ["data engineer", "data scientist", "data analyst"]
    )
    
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        resume_text = ""
        for page_num in range(len(pdf_reader.pages)):
            resume_text += pdf_reader.pages[page_num].extract_text()
        
        st.success("Resume uploaded successfully!")
        
        with st.expander("See extracted text"):
            st.write(resume_text)

        if st.button("Analyze My Resume"):
            with st.spinner("Analyzing your resume..."):
                from groq import Groq
                
                groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                
                resume_prompt = f"""
                Extract skills from this resume and return ONLY a JSON object:
                - technical_skills: list of technical skills
                - cloud_platforms: list of cloud platforms
                - experience_years: total years of experience as a number
                - experience_level: one of "entry", "mid", "senior"
                - education: highest education level
                
                Resume:
                {resume_text}
                
                Return ONLY valid JSON. No explanation.
                """
                
                response = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": resume_prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0
                )
                
                response_text = response.choices[0].message.content.strip()
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                resume_skills = json.loads(response_text)
                
                st.subheader("Your Skills Profile")
                st.json(resume_skills)
                
                st.subheader("Gap Analysis")
                st.markdown(f"Comparing your skills against market demand for **{target_role}**")
                
                conn = get_connection()
                df_market = pd.read_sql("""
                    SELECT skill, COUNT(*) as demand_count
                    FROM (
                        SELECT js.job_id, j.role, json_array_elements_text(js.technical_skills::json) as skill
                        FROM job_skills js
                        JOIN jobs j ON js.job_id = j.job_id
                        WHERE j.role = %(role)s
                    ) skills
                    GROUP BY skill
                    ORDER BY demand_count DESC
                    LIMIT 20
                """, conn, params={"role": target_role})
                conn.close()
                
                user_skills = [s.lower() for s in resume_skills.get("technical_skills", [])]
                market_skills = df_market["skill"].str.lower().tolist()
                
                missing_skills = [s for s in market_skills if s not in user_skills]
                matching_skills = [s for s in market_skills if s in user_skills]
                
                match_percentage = round(len(matching_skills) / len(market_skills) * 100)
                
                st.metric("Resume Match Score", f"{match_percentage}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"Skills you have ({len(matching_skills)})")
                    for skill in matching_skills:
                        st.write(f"✅ {skill}")
                
                with col2:
                    st.error(f"Skills to add ({len(missing_skills)})")
                    for skill in missing_skills:
                        st.write(f"❌ {skill}")