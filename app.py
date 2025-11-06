import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re

# Page configuration
st.set_page_config(
    page_title="🙏 Daily Gratitude Tracker",
    page_icon="🌱",
    layout="centered"
)

# Fixed CSS with better contrast
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        color: #4682B4;
        border-bottom: 2px solid #E8F5E8;
        padding-bottom: 0.5rem;
    }
    .gratitude-card {
        background: linear-gradient(135deg, #E8F5E8, #F0FFF0);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #2E8B57;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .gratitude-card strong {
        color: #2E8B57 !important;
    }
    .gratitude-card p {
        color: #333333 !important;
        font-size: 1.1em;
        line-height: 1.5;
        margin: 1rem 0;
    }
    .gratitude-card small {
        color: #666666 !important;
    }
    .mood-indicator {
        font-size: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        color: #000000 !important;
    }
    .stats-card strong {
        color: #2E8B57 !important;
    }
    .achievement-card {
        background: #FFD70020;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #FFD700;
        color: #000000 !important;
    }
    .achievement-card strong {
        color: #B8860B !important;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<div class="main-header">🙏 Daily Gratitude Tracker</div>', unsafe_allow_html=True)
st.markdown("### 🌱 Cultivate gratitude, track your happiness, and watch your mood bloom")

# Initialize session state
if 'entries' not in st.session_state:
    st.session_state.entries = []
if 'streak' not in st.session_state:
    st.session_state.streak = 0

# Sidebar navigation
st.sidebar.title("🌿 Navigation")
page = st.sidebar.selectbox(
    "Choose Page",
    ["📝 Today's Entry", "📊 Mood Analytics", "🌼 Gratitude Journal", "🏆 Achievements"]
)

# Main app functionality
if page == "📝 Today's Entry":
    st.markdown('<div class="sub-header">📝 Your Gratitude Journey Starts Today</div>', unsafe_allow_html=True)
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        gratitude_text = st.text_area(
            "What are you grateful for today?",
            placeholder="I'm grateful for... the sunshine, my health, a good conversation, learning something new...",
            height=100
        )
    
    with col2:
        mood_level = st.slider("How's your mood today?", 1, 10, 7, 
                              help="1 = Very Low, 10 = Excellent")
        
        # Mood emoji display
        mood_emojis = ["😢", "😔", "😐", "🙂", "😊", "😄", "🥰", "🤩", "🌈", "✨"]
        st.markdown(f'<div class="mood-indicator">{mood_emojis[mood_level-1]}</div>', unsafe_allow_html=True)
    
    # Tags
    tags = st.multiselect(
        "Categories (optional):",
        ["Family", "Friends", "Health", "Nature", "Work", "Learning", "Hobbies", "Food", "Random Acts", "Personal Growth"],
        help="What areas of life does this gratitude relate to?"
    )
    
    # Save entry
    if st.button("💾 Save Today's Gratitude", type="primary", use_container_width=True):
        if gratitude_text.strip():
            entry = {
                "date": datetime.now(),
                "gratitude": gratitude_text.strip(),
                "mood": mood_level,
                "tags": tags,
                "word_count": len(gratitude_text.split())
            }
            st.session_state.entries.append(entry)
            
            # Update streak
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            if st.session_state.entries:
                last_entry_date = st.session_state.entries[-2]["date"].date() if len(st.session_state.entries) > 1 else None
                if last_entry_date == yesterday:
                    st.session_state.streak += 1
                elif last_entry_date != today:
                    st.session_state.streak = 1
            else:
                st.session_state.streak = 1
            
            st.balloons()
            st.success("🎉 Gratitude entry saved! Your future self will thank you.")
        else:
            st.warning("Please write something you're grateful for!")

# Analytics Page
elif page == "📊 Mood Analytics":
    st.markdown('<div class="sub-header">📊 Your Gratitude & Mood Patterns</div>', unsafe_allow_html=True)
    
    if not st.session_state.entries:
        st.info("🌟 Start your gratitude journey by making your first entry!")
    else:
        # Create DataFrame
        df = pd.DataFrame(st.session_state.entries)
        df['date'] = pd.to_datetime(df['date'])
        df['day_name'] = df['date'].dt.day_name()
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stats-card">📅<br><strong>Total Entries</strong><br>{}</div>'.format(
                len(df)), unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">😊<br><strong>Avg Mood</strong><br>{:.1f}/10</div>'.format(
                df['mood'].mean()), unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stats-card">🔥<br><strong>Current Streak</strong><br>{} days</div>'.format(
                st.session_state.streak), unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="stats-card">📝<br><strong>Avg Words</strong><br>{:.0f}</div>'.format(
                df['word_count'].mean()), unsafe_allow_html=True)
        
        # Mood trend chart
        st.subheader("📈 Mood Trend Over Time")
        fig_mood = px.line(df, x='date', y='mood', 
                          title="How Your Mood Has Changed",
                          markers=True)
        fig_mood.update_traces(line=dict(color='#2E8B57', width=3))
        fig_mood.update_layout(yaxis_range=[1,10])
        st.plotly_chart(fig_mood, use_container_width=True)
        
        # Word cloud
        st.subheader("🌤️ Your Gratitude Word Cloud")
        all_text = ' '.join(df['gratitude'].tolist())
        if all_text.strip():
            # Clean text and create word cloud
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            word_freq = Counter(words)
            
            if word_freq:
                col1, col2 = st.columns([2, 1])
                with col1:
                    # Create word cloud
                    wc = WordCloud(width=400, height=200, background_color='white', 
                                  colormap='Greens').generate_from_frequencies(word_freq)
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                
                with col2:
                    st.write("**Most Common Words:**")
                    for word, count in word_freq.most_common(5):
                        st.write(f"• {word.title()} ({count})")
        
        # Mood by day of week
        st.subheader("📅 Mood by Day of the Week")
        if len(df) > 1:
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            mood_by_day = df.groupby('day_name')['mood'].mean().reindex(day_order)
            
            fig_day = px.bar(x=mood_by_day.index, y=mood_by_day.values,
                           title="Average Mood by Day of Week",
                           color=mood_by_day.values,
                           color_continuous_scale='Greens')
            fig_day.update_layout(xaxis_title="Day of Week", yaxis_title="Average Mood")
            st.plotly_chart(fig_day, use_container_width=True)

# Journal Page
elif page == "🌼 Gratitude Journal":
    st.markdown('<div class="sub-header">🌼 Your Gratitude Journal</div>', unsafe_allow_html=True)
    
    if not st.session_state.entries:
        st.info("Your journal is waiting for your first entry! 🌟")
    else:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            sort_order = st.selectbox("Sort by:", ["Newest First", "Oldest First"])
        with col2:
            mood_filter = st.selectbox("Filter by mood:", ["All Moods", "High (8-10)", "Medium (4-7)", "Low (1-3)"])
        
        # Filter and sort entries
        filtered_entries = st.session_state.entries.copy()
        
        # Apply mood filter
        if mood_filter == "High (8-10)":
            filtered_entries = [e for e in filtered_entries if e['mood'] >= 8]
        elif mood_filter == "Medium (4-7)":
            filtered_entries = [e for e in filtered_entries if 4 <= e['mood'] <= 7]
        elif mood_filter == "Low (1-3)":
            filtered_entries = [e for e in filtered_entries if e['mood'] <= 3]
        
        # Sort entries
        if sort_order == "Newest First":
            filtered_entries.reverse()
        
        # Display entries
        for i, entry in enumerate(filtered_entries):
            mood_emojis = ["😢", "😔", "😐", "🙂", "😊", "😄", "🥰", "🤩", "🌈", "✨"]
            
            st.markdown(f"""
            <div class="gratitude-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>📅 {entry['date'].strftime('%B %d, %Y')}</strong>
                    <span style="font-size: 1.5rem;">{mood_emojis[entry['mood']-1]} {entry['mood']}/10</span>
                </div>
                <p style="margin: 1rem 0; font-size: 1.1em;">{entry['gratitude']}</p>
                <div style="color: #666; font-size: 0.9em;">
                    {', '.join(entry['tags']) if entry['tags'] else 'No tags'}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Achievements Page
else:
    st.markdown('<div class="sub-header">🏆 Your Gratitude Achievements</div>', unsafe_allow_html=True)
    
    if not st.session_state.entries:
        st.info("Start your gratitude journey to unlock achievements! 🌟")
    else:
        df = pd.DataFrame(st.session_state.entries)
        
        # Achievement checks
        achievements = []
        
        # Streak achievements
        if st.session_state.streak >= 7:
            achievements.append(("🔥 7-Day Streak", "Consistent gratitude for a week!", "gold"))
        elif st.session_state.streak >= 3:
            achievements.append(("⭐ 3-Day Streak", "Building a great habit!", "silver"))
        
        # Entry count achievements
        if len(df) >= 10:
            achievements.append(("📚 10 Entries", "A decade of gratitude!", "gold"))
        elif len(df) >= 5:
            achievements.append(("📖 5 Entries", "Halfway to a decade!", "silver"))
        
        # Mood achievements
        if df['mood'].mean() >= 8:
            achievements.append(("😊 Positive Vibes", "Consistently high mood!", "gold"))
        
        # Word count achievements
        if df['word_count'].mean() >= 20:
            achievements.append(("🗣️ Eloquent", "Detailed gratitude entries!", "silver"))
        
        # Display achievements
        if achievements:
            st.success("🎉 You've unlocked these achievements:")
            for name, desc, level in achievements:
                color = "#FFD700" if level == "gold" else "#C0C0C0"
                st.markdown(f"""
                <div class="achievement-card">
                    <strong>{name}</strong><br>
                    <small>{desc}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Keep going! You're on your way to unlocking achievements.")
        
        # Progress bars
        st.subheader("📊 Your Progress")
        
        # Streak progress
        streak_progress = min(st.session_state.streak / 7, 1.0)
        st.write(f"**7-Day Streak:** {st.session_state.streak}/7 days")
        st.progress(streak_progress)
        
        # Entries progress
        entries_progress = min(len(df) / 10, 1.0)
        st.write(f"**10 Entries Milestone:** {len(df)}/10 entries")
        st.progress(entries_progress)

# Sidebar tips and info
st.sidebar.markdown("---")
st.sidebar.subheader("💡 The Science of Gratitude")
st.sidebar.write("""
Research shows that practicing gratitude:
- 🧠 **Reduces stress** and anxiety
- 😊 **Increases happiness** levels
- 💪 **Strengthens relationships**
- 🌙 **Improves sleep** quality

*Just 5 minutes a day can make a difference!*
""")

# Show quick stats in sidebar
if st.session_state.entries:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Quick Stats")
    total_conversions = len(st.session_state.entries)
    st.sidebar.write(f"Total Entries: **{total_conversions}**")
    st.sidebar.write(f"Current Streak: **{st.session_state.streak} days**")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "Made with ❤️ to spread positivity | Your data stays private and secure"
    "</div>",
    unsafe_allow_html=True
)