import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()

# Configuration
st.set_page_config(page_title="Exam Coach AI", page_icon="🎓", layout="wide")
API_BASE_URL = "http://127.0.0.1:8000/api"

# Removed custom CSS

def initialize_session():
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'profile_id' not in st.session_state:
        st.session_state.profile_id = None
    if 'weak_topics' not in st.session_state:
        st.session_state.weak_topics = []
    if 'plan' not in st.session_state:
        st.session_state.plan = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def navigate_to(page):
    st.session_state.page = page

def require_profile():
    if st.session_state.profile_id is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## Welcome to Agent Coach")
            st.markdown("Let's set up your profile")
            
            with st.container():
                with st.form("profile_form"):
                    exam_type = st.text_input("Which exam are you preparing for?", placeholder="e.g., JEE, NEET, GRE")
                    target = st.text_input("What is your target score or rank?", placeholder="e.g., 99th Percentile")
                    submit = st.form_submit_button("Get Started", type="primary", use_container_width=True)
                    
                    if submit:
                        if not exam_type or not target:
                            st.error("Please fill all fields.")
                        else:
                            with st.spinner("Setting up your dashboard..."):
                                try:
                                    response = requests.post(f"{API_BASE_URL}/profile", json={
                                        "exam_type": exam_type,
                                        "target_marks_rank": target
                                    })
                                    if response.status_code == 200:
                                        st.session_state.profile_id = response.json().get("id")
                                        st.success("Profile created successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to save profile.")
                                except Exception as e:
                                    st.error(f"Error: {e}")
        return False
    return True

# --- PAGE: HOME ---

def show_home():
    st.markdown("# Agent Coach")
    st.markdown("### Your AI Companion for Competitive Exams")
    st.markdown("Analyze mock tests, create personalized study plans, track progress, access free resources, and chat with AI tutors.")
    st.markdown("---")
    
    col3, col4, col5, col6 = st.columns(4, gap="large")
    
    with col3:
        st.markdown("### 📊 Analyze")
        st.write("Understand your mistakes in mock tests.")
        if st.button("Start Analysis →", key="btn_analyze", use_container_width=True):
            navigate_to("analyze")
            st.rerun()
            
    with col4:
        st.markdown("### 📅 Plan")
        st.write("Get your optimized 7-day study plan.")
        if st.button("Generate Plan →", key="btn_plan", use_container_width=True):
            navigate_to("plan")
            st.rerun()

    with col5:
        st.markdown("### 📈 Dashboard")
        st.write("Track progress and review resources.")
        if st.button("View Dashboard →", key="btn_dashboard", use_container_width=True):
            navigate_to("dashboard")
            st.rerun()

    with col6:
        st.markdown("### 💬 Ask AI")
        st.write("Get answers from your tutor.")
        if st.button("Ask Question →", key="btn_chat", use_container_width=True):
            navigate_to("chat")
            st.rerun()

# --- PAGE: ANALYZE ---

def show_analyze():
    st.button("← Back to Home", on_click=navigate_to, args=("home",))
    st.markdown("## 📊 Mock Test Analysis")
    
    if not require_profile():
        return
        
    st.markdown("Paste your mock test results or errors.")
    test_result = st.text_area("Mock Test Results / Errors", height=200, 
                             placeholder="e.g. Q1: Calculation error...")
    
    if st.button("Analyze Weaknesses", type="primary"):
        if not test_result:
            st.warning("Please enter your test results.")
        else:
            with st.spinner("Analyzing with AI..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/analyze-test", json={
                        "student_id": st.session_state.profile_id,
                        "test_result_text": test_result
                    })
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.weak_topics = data.get("weak_topics", [])
                        st.success("Analysis Complete!")
                    else:
                        st.error(f"Analysis failed")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    if st.session_state.weak_topics:
        st.markdown("### 🎯 Identified Weak Topics & Resources")
        for topic in st.session_state.weak_topics:
            st.markdown(f"#### 📖 **{topic}**")
            
            with st.spinner(f"Finding open resources for {topic}..."):
                try:
                    res = requests.get(f"{API_BASE_URL}/resources/topic/{topic}")
                    if res.status_code == 200:
                        resources = res.json()
                        if resources:
                            for item in resources:
                                col1, col2, col3 = st.columns([6, 2, 2])
                                with col1:
                                    st.markdown(f"**{item.get('title', 'Unknown')}** ({item.get('source', 'Web')})  \n<small>{item.get('description', '')}</small>", unsafe_allow_html=True)
                                with col2:
                                    st.link_button("↗ Open", item.get("url", "#"), use_container_width=True)
                                with col3:
                                    likes = item.get("likes") or 0
                                    if st.button(f"👍 {likes}", key=f"like_analyze_{item.get('id')}", use_container_width=True):
                                        requests.post(f"{API_BASE_URL}/resources/{item.get('id')}/like")
                                        st.rerun()
                        else:
                            st.info("No resources found.")
                except Exception as e:
                    st.error(f"Error loading resources: {e}")
            st.markdown("---")
            
        st.info("Go to Dashboard or Plan to start improving!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Resources →"):
                navigate_to("recommendations")
                st.rerun()
        with col2:
            if st.button("Go to 7-Day Plan →"):
                navigate_to("plan")
                st.rerun()

# --- PAGE: PLAN ---

def show_plan():
    st.button("← Back to Home", on_click=navigate_to, args=("home",))
    st.markdown("## 📅 7-Day Revision Plan")
    
    if not require_profile():
        return
        
    st.markdown("Set your daily availability for a personalized timetable.")
    
    with st.form("revision_form"):
        col1, col2 = st.columns(2)
        with col1:
            weekday_hrs = st.number_input("Study hours (Weekdays)", min_value=1.0, max_value=16.0, value=4.0, step=0.5)
        with col2:
            weekend_hrs = st.number_input("Study hours (Weekends)", min_value=1.0, max_value=16.0, value=8.0, step=0.5)
        
        generate_plan_btn = st.form_submit_button("Generate Timetable", type="primary")
        
    if generate_plan_btn:
        if not st.session_state.weak_topics:
            st.warning("Please analyze a mock test first.")
            if st.button("Go to Analysis"):
                navigate_to("analyze")
                st.rerun()
        else:
            with st.spinner("Crafting your strategy..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/revision-plan", json={
                        "student_id": st.session_state.profile_id,
                        "weekday_hours": weekday_hrs,
                        "weekend_hours": weekend_hrs
                    })
                    if response.status_code == 200:
                        st.session_state.plan = response.json().get("plan_text")
                        st.success("Your timetable is ready!")
                    else:
                        st.error(f"Failed to generate plan")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    if st.session_state.plan:
        st.markdown("### 📋 Your Timetable Overview")
        st.info("💡 **Goal-Oriented Plan:** Specifically calibrated for your weak topics.")
        
        try:
            plan_data = json.loads(st.session_state.plan)
            
            if isinstance(plan_data, dict) and "plan" in plan_data:
                df_data = []
                for item in plan_data["plan"]:
                    df_data.append({
                        "Day": item.get("day", ""),
                        "Subject": item.get("subject", ""),
                        "Topic": item.get("topic", ""),
                        "Time": item.get("time", "")
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("### 📌 Detailed Study Focus")
                
                for item in plan_data["plan"]:
                    day = item.get("day", "")
                    subject = item.get("subject", "")
                    topic = item.get("topic", "")
                    with st.expander(f"View – {day}: {subject} ({topic})"):
                        for focus_point in item.get("focus", []):
                            st.markdown(f"• {focus_point}")
            else:
                with st.expander("Show Detailed Timetable", expanded=True):
                    st.markdown(st.session_state.plan)
        except:
            with st.expander("Show Detailed Timetable", expanded=True):
                st.markdown(st.session_state.plan)

# --- PAGE: RECOMMENDATIONS (with Resources) ---

def show_recommendations():
    st.button("← Back to Home", on_click=navigate_to, args=("home",))
    st.markdown("## 📚 Topic Resources & Recommendations")
    
    if not require_profile():
        return
    
    if not st.session_state.weak_topics:
        st.warning("Please analyze a mock test first to see resources.")
        if st.button("Go to Analysis"):
            navigate_to("analyze")
            st.rerun()
        return
    
    # Select a topic
    selected_topic = st.selectbox("Select a topic to view resources", st.session_state.weak_topics)
    
    if selected_topic:
        st.markdown(f"### 📖 Resources for: **{selected_topic}**")
        
        with st.spinner(f"Loading resources for {selected_topic}..."):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/resources/topic/{selected_topic}",
                    params={"exam_type": "JEE"}  # Adjust based on profile
                )
                
                if response.status_code == 200:
                    resources = response.json()
                    
                    if resources:
                        # Group resources by type
                        resource_types = {}
                        for resource in resources:
                            res_type = resource.get("resource_type", "Other")
                            if res_type not in resource_types:
                                resource_types[res_type] = []
                            resource_types[res_type].append(resource)
                        
                        # Display by type
                        for res_type, items in resource_types.items():
                            st.markdown(f"#### 📌 {res_type.replace('_', ' ').title()}")
                            
                            for item in items:
                                with st.container():
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(f"**{item.get('title', 'Untitled')}**  \n<small>{item.get('description', '')}</small>  \n<small>Source: {item.get('source', 'Unknown')} | Difficulty: {item.get('difficulty_level', 'N/A')}</small>", unsafe_allow_html=True)
                                    with col2:
                                        if st.button("Visit", key=f"resource_{item.get('id', 0)}", use_container_width=True):
                                            st.info(f"[Open Resource]({item.get('url', '#')})")
                    else:
                        st.info("No resources found for this topic yet. Check back soon!")
                        st.markdown("**Suggested Resources:**")
                        st.markdown("""
                        - **YouTube:** Search for '[Topic] [Exam] tutorial'
                        - **Khan Academy:** Comprehensive video lessons
                        - **Brilliant.org:** Interactive problem solving
                        - **Course websites:** Study materials and practice tests
                        """)
                else:
                    st.error("Failed to load resources")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Quick action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Track Progress"):
                navigate_to("dashboard")
                st.rerun()
        with col2:
            if st.button("💬 Ask AI About This"):
                navigate_to("chat")
                st.rerun()
        with col3:
            if st.button("← Back to Topics"):
                st.rerun()

# --- PAGE: DASHBOARD ---

def show_dashboard():
    st.button("← Back to Home", on_click=navigate_to, args=("home",))
    st.markdown("## 📊 Student Dashboard")
    
    if not require_profile():
        return
    
    with st.spinner("Loading dashboard..."):
        try:
            response = requests.get(f"{API_BASE_URL}/dashboard/{st.session_state.profile_id}")
            
            if response.status_code == 200:
                dashboard = response.json()
                
                # Stats Cards
                stats = dashboard.get("stats", {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Topics", stats.get("total_topics", 0))
                
                with col2:
                    st.metric("Topics Completed", stats.get("topics_completed", 0))
                
                with col3:
                    st.metric("Study Hours", f"{stats.get('total_study_hours', 0):.1f}")
                
                with col4:
                    st.metric("Progress", f"{stats.get('overall_progress_percentage', 0):.0f}%")
                
                st.markdown("---")
                
                # --- NEW ANALYTICS SECTION ---
                analytics = dashboard.get("analytics", {})
                if analytics:
                    try:
                        import plotly.express as px
                    
                        st.markdown("### 📊 Performance Analytics")
                        
                        # 7 Demo Tests Trend (Line Chart)
                        demo_tests = analytics.get("demo_tests", [])
                        if demo_tests:
                            st.markdown("#### Recent 7 Mock Tests Trend")
                            df_tests = pd.DataFrame(demo_tests)
                            df_tests.set_index("Date", inplace=True)
                            st.line_chart(df_tests["Score"])
                        
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            # Correct vs Incorrect (Pie Chart)
                            st.markdown("#### Accuracy Breakdown")
                            accuracy = analytics.get("accuracy", {})
                            if accuracy:
                                df_acc = pd.DataFrame(list(accuracy.items()), columns=["Type", "Count"])
                                fig_pie = px.pie(df_acc, values="Count", names="Type", hole=0.4, color="Type",
                                              color_discrete_map={"Correct": "#22c55e", "Incorrect": "#ef4444", "Unattempted": "#cbd5e1"})
                                fig_pie.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                                st.plotly_chart(fig_pie, use_container_width=True)
                                
                        with col_chart2:
                            # Error Analysis (Bar Chart)
                            st.markdown("#### Error Analysis (Why you lost marks)")
                            error_types = analytics.get("error_types", {})
                            if error_types:
                                df_errors = pd.DataFrame(list(error_types.items()), columns=["Error Type", "Count"])
                                fig_bar = px.bar(df_errors, x="Error Type", y="Count", color="Error Type")
                                fig_bar.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
                                st.plotly_chart(fig_bar, use_container_width=True)
                        
                        # Weak Questions Breakdown
                        weak_qs = analytics.get("weak_questions", [])
                        if weak_qs:
                            st.markdown("#### Top 10 Weak Topics (By Missed Questions)")
                            df_weak = pd.DataFrame(weak_qs)
                            if not df_weak.empty:
                                df_display = df_weak.sort_values(by="questions_missed", ascending=False).head(10)
                                fig_weak = px.bar(df_display, x="topic", y="questions_missed", color="subject", 
                                                 title="Missed Questions Source",
                                                 labels={"questions_missed": "Errors", "topic": "Topic", "subject": "Subject"})
                                st.plotly_chart(fig_weak, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error rendering analytics charts: {e}")

                st.markdown("---")
                
                # Progress by Topic
                st.markdown("### 📈 Progress by Topic")
                topics = dashboard.get("topics", [])
                
                if topics:
                    for topic in topics:
                        status = topic.get("status", "pending")
                        progress = topic.get("progress_percentage", 0)
                        
                        st.markdown(f"**{topic.get('topic', 'Unknown')}**  \nProgress: {progress:.0f}% | Status: {status.replace('_', ' ').title()}")
                        if topic.get('last_studied'):
                            st.caption(f"Last Studied: {topic.get('last_studied')}")
                        
                        # Show resources
                        resources = topic.get("free_resources", [])
                        if resources:
                            with st.expander(f"📚 View {len(resources)} resource(s) for {topic.get('topic')}"):
                                for resource in resources[:3]:  # Show first 3
                                    st.markdown(f"""
                                    - **{resource.get('title', 'Resource')}**  
                                      {resource.get('description', '')}  
                                      [Learn more]({resource.get('url', '#')})
                                    """)
                else:
                    st.info("No progress recorded yet. Start analyzing mock tests to begin tracking!")
                
                st.markdown("---")
                
                # Recent Chat Activity
                st.markdown("### 💬 Recent Q&A Activity")
                recent_chats = dashboard.get("recent_chats", [])
                
                if recent_chats:
                    for chat in recent_chats[:5]:
                        with st.expander(f"Q: {chat.get('question', '')[:60]}..."):
                            st.write(f"**Question:** {chat.get('question', '')}")
                            st.write(f"**Answer:** {chat.get('answer', '')[:300]}...")
                            st.caption(f"Asked on: {chat.get('created_at', '')}")
                else:
                    st.info("No Q&A activity yet. Ask questions to get AI help!")
                
                # Action buttons
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📚 View Resources"):
                        navigate_to("recommendations")
                        st.rerun()
                with col2:
                    if st.button("💬 Ask AI"):
                        navigate_to("chat")
                        st.rerun()
                with col3:
                    if st.button("🔄 Refresh"):
                        st.rerun()
                
            else:
                st.error(f"Failed to load dashboard data. API returned status code {response.status_code}.")
                        
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")

# --- PAGE: AI CHATBOT (Q&A) ---

def show_chat():
    st.button("← Back to Home", on_click=navigate_to, args=("home",))
    st.markdown("## 💬 Ask AI Tutor")
    
    if not require_profile():
        return
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input("Ask me anything about your exam topics:", placeholder="e.g., How to solve integration by parts?")
    with col2:
        topic = st.text_input("Topic (optional)", placeholder="e.g., Calculus")
    
    if st.button("Get Answer", type="primary", use_container_width=True):
        if not question:
            st.warning("Please ask a question!")
        else:
            with st.spinner("AI tutor is thinking..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/chat/ask", json={
                        "student_id": st.session_state.profile_id,
                        "question": question,
                        "topic": topic if topic else None
                    })
                    
                    if response.status_code == 200:
                        chat_data = response.json()
                        st.session_state.chat_history.insert(0, chat_data)
                        st.success("Answer ready below!")
                    else:
                        st.error("Failed to get answer")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📝 Conversation History")
        
        for chat in st.session_state.chat_history:
            with st.expander(f"Q: {chat.get('question', '')[:60]}..."):
                st.write(f"**Question:** {chat.get('question', '')}")
                st.markdown(f"**Answer:**")
                st.markdown(chat.get('answer', ''))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Helpful", key=f"helpful_{chat.get('id')}"):
                        # Send feedback
                        try:
                            requests.post(f"{API_BASE_URL}/chat/feedback", json={
                                "chat_id": chat.get('id'),
                                "helpful": True
                            })
                            st.success("Thanks for the feedback!")
                        except:
                            pass
                
                with col2:
                    if st.button("👎 Not helpful", key=f"not_helpful_{chat.get('id')}"):
                        try:
                            requests.post(f"{API_BASE_URL}/chat/feedback", json={
                                "chat_id": chat.get('id'),
                                "helpful": False
                            })
                            st.info("We'll improve!")
                        except:
                            pass
    else:
        st.info("Ask questions to start building your conversation history!")

# --- PAGE: MULTI-SHEET UPLOAD ---

def show_multisheet():
    st.button("← Back to Home", on_click=navigate_to, args=("home",))
    st.markdown("## 🗂️ Multi-Sheet Upload & Analysis")
    
    if not require_profile():
        return

    st.markdown("Upload multiple mock tests to find cross-sheet error patterns.")
    
    # Upload section
    uploaded_files = st.file_uploader("Upload Mock Tests (TXT, CSV, PDF)", accept_multiple_files=True)
    if st.button("Upload Files", type="primary"):
        if not uploaded_files:
            st.warning("Please select files before uploading.")
        else:
            with st.spinner("Uploading sheets..."):
                try:
                    files_to_upload = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                    response = requests.post(
                        f"{API_BASE_URL}/sheets/upload",
                        data={"student_id": st.session_state.profile_id},
                        files=files_to_upload
                    )
                    if response.status_code == 200:
                        st.success(f"{response.json().get('uploaded')} sheets uploaded successfully!")
                    else:
                        st.error("Upload failed")
                except Exception as e:
                    st.error(f"Error connecting to server: {e}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analyze Error Patterns"):
            with st.spinner("Analyzing patterns across all your sheets..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/sheets/analyze-patterns/{st.session_state.profile_id}")
                    if res.status_code == 200:
                        st.success(f"Found {res.json().get('patterns_found')} recurring error patterns!")
                    else:
                        st.error(f"Analysis failed: {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        if st.button("Refresh Saved Documents"):
            st.rerun()

    st.markdown("---")
    
    # History of patterns
    st.markdown("### 🔍 Your Error Patterns")
    try:
        pat_res = requests.get(f"{API_BASE_URL}/sheets/patterns/{st.session_state.profile_id}")
        if pat_res.status_code == 200:
            patterns = pat_res.json()
            if patterns:
                for p in patterns:
                    severity_color = "🔴" if p['severity'] == "high" else ("🟠" if p['severity'] == "medium" else "🟢")
                    with st.expander(f"{severity_color} {p['topic']} - {p['error_type']} (Found {p['frequency']} times)"):
                        st.markdown(f"**Description:** {p['description']}")
                        st.markdown(f"**Fix Suggestion:** {p['suggestion']}")
            else:
                st.info("No error patterns found yet. Upload files and click analyze!")
    except:
        pass


# --- PAGE: WHATSAPP REMINDERS ---

def show_reminders():
    st.button("← Back to Home", on_click=navigate_to, args=("home",))
    st.markdown("## 🔔 WhatsApp Reminders")
    
    if not require_profile():
        return

    st.markdown("Configure WhatsApp notifications for study plans and analysis.")
    st.warning("Make sure WhatsApp Web is open and logged in on the backend host (Chrome browser) before sending.")
    
    # Load current settings
    settings = {"configured": False}
    try:
        res = requests.get(f"{API_BASE_URL}/reminders/settings/{st.session_state.profile_id}")
        if res.status_code == 200:
            settings = res.json()
    except Exception:
        pass

    with st.form("reminder_settings"):
        default_phone = settings.get("phone_number", "+91")
        default_time = settings.get("reminder_time", "07:00")
        is_active = settings.get("is_active", True)
        existing_types = settings.get("reminder_types", "daily,plan,analysis").split(",") if settings.get("configured") else ["daily", "plan", "analysis"]
        
        phone = st.text_input("WhatsApp Number with country code", value=default_phone, placeholder="+919876543210")
        time = st.time_input("Daily Reminder Time", value=pd.to_datetime(default_time).time())
        active = st.checkbox("Enable WhatsApp Reminders", value=is_active)
        
        type_options = ["daily", "plan", "analysis", "discussion"]
        selected_types = st.multiselect("Notify me on:", type_options, default=existing_types)
        
        if st.form_submit_button("Save Settings", type="primary"):
            try:
                save_res = requests.post(
                    f"{API_BASE_URL}/reminders/settings",
                    params={
                        "student_id": st.session_state.profile_id,
                        "phone_number": phone,
                        "reminder_time": time.strftime("%H:%M"),
                        "reminder_types": ",".join(selected_types),
                        "is_active": active
                    }
                )
                if save_res.status_code == 200:
                    st.success("Settings saved successfully!")
                    st.rerun()
                else:
                    st.error("Could not save settings.")
            except Exception as e:
                st.error(f"Error: {e}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send Test Message"):
            with st.spinner("Sending test WhatsApp message..."):
                try:
                    test_res = requests.post(f"{API_BASE_URL}/reminders/test/{st.session_state.profile_id}")
                    if test_res.status_code == 200:
                        st.success("Test message sent successfully!")
                    else:
                        st.error(f"Failed to send: {test_res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    with col2:
        if st.button("Send Daily Reminder manually"):
            with st.spinner("Sending daily reminder..."):
                try:
                    daily_res = requests.post(f"{API_BASE_URL}/reminders/send-daily/{st.session_state.profile_id}")
                    if daily_res.status_code == 200:
                        st.success("Daily reminder sent successfully!")
                    else:
                        st.error(f"Failed to send: {daily_res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("### 📋 Notification History")
    try:
        logs_res = requests.get(f"{API_BASE_URL}/reminders/logs/{st.session_state.profile_id}")
        if logs_res.status_code == 200:
            logs = logs_res.json()
            if logs:
                df = pd.DataFrame(logs)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No notifications sent yet.")
    except:
        pass


# --- MAIN ---

def main():
    initialize_session()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎓 Navigation")
        if st.button("🏠 Home", use_container_width=True):
            navigate_to("home")
            st.rerun()
        if st.session_state.profile_id:
            if st.button("📊 Analyze", use_container_width=True):
                navigate_to("analyze")
                st.rerun()
            if st.button("📅 7-Day Plan", use_container_width=True):
                navigate_to("plan")
                st.rerun()
            if st.button("📚 Resources", use_container_width=True):
                navigate_to("recommendations")
                st.rerun()
            if st.button("📈 Dashboard", use_container_width=True):
                navigate_to("dashboard")
                st.rerun()
            if st.button("🗂️ Multi-Sheet", use_container_width=True):
                navigate_to("multisheet")
                st.rerun()
            if st.button("🔔 Reminders", use_container_width=True):
                navigate_to("reminders")
                st.rerun()
            if st.button("💬 Ask AI", use_container_width=True):
                navigate_to("chat")
                st.rerun()
    
    # Page routing
    if st.session_state.page == "home":
        show_home()
    elif st.session_state.page == "analyze":
        show_analyze()
    elif st.session_state.page == "plan":
        show_plan()
    elif st.session_state.page == "recommendations":
        show_recommendations()
    elif st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "chat":
        show_chat()
    elif st.session_state.page == "multisheet":
        show_multisheet()
    elif st.session_state.page == "reminders":
        show_reminders()

if __name__ == "__main__":
    main()
