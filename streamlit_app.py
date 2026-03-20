import streamlit as st
import anthropic
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TwoSidedNews",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600&display=swap');

  /* Global */
  .stApp { background-color: #07090F; color: #E8EDF5; }
  .block-container { padding: 2rem 3rem; max-width: 1200px; }

  /* Hide default streamlit elements */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* Header */
  .tsn-header {
    display: flex; align-items: center; gap: 16px;
    padding: 24px 0 8px 0; margin-bottom: 8px;
  }
  .tsn-logo { font-size: 40px; }
  .tsn-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem; font-weight: 900;
    background: linear-gradient(90deg, #2463EB, #F8FAFC, #DC2626);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.1;
  }
  .tsn-tagline {
    font-family: 'Inter', sans-serif; font-size: 0.95rem;
    color: #64748B; margin: 0; font-style: italic;
  }
  .tsn-divider {
    height: 3px;
    background: linear-gradient(90deg, #2463EB 0%, #D97706 50%, #DC2626 100%);
    border: none; border-radius: 2px; margin: 16px 0 28px 0;
  }

  /* Cards */
  .card {
    background: #0D111C; border: 1px solid #1E293B;
    border-radius: 12px; padding: 20px 22px;
    margin-bottom: 16px;
  }
  .card-left  { border-left: 4px solid #2463EB; }
  .card-right { border-left: 4px solid #DC2626; }
  .card-center{ border-left: 4px solid #059669; }
  .card-amber { border-left: 4px solid #D97706; }
  .card-purple{ border-left: 4px solid #7C3AED; }

  /* Section labels */
  .section-tag {
    font-family: 'Inter', sans-serif; font-size: 10px;
    font-weight: 700; letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 8px;
  }
  .tag-blue   { color: #2463EB; }
  .tag-red    { color: #DC2626; }
  .tag-green  { color: #059669; }
  .tag-amber  { color: #D97706; }
  .tag-purple { color: #7C3AED; }

  /* Big stat */
  .big-stat {
    font-family: 'Playfair Display', serif;
    font-size: 3rem; font-weight: 900; line-height: 1;
  }
  .stat-label {
    font-size: 0.75rem; color: #64748B;
    text-transform: uppercase; letter-spacing: 1px;
  }

  /* Risk badge */
  .risk-low    { background: #0D2A1E; border: 1px solid #1A4A2E; color: #10B981; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; }
  .risk-medium { background: #2A1E0D; border: 1px solid #4A2E1A; color: #F59E0B; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; }
  .risk-high   { background: #2A0D0D; border: 1px solid #4A1A1A; color: #EF4444; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; }

  /* Loaded word tags */
  .word-tag {
    display: inline-block; background: #2A1A0D; border: 1px solid #4A2E0D;
    color: #F59E0B; padding: 3px 10px; border-radius: 6px;
    font-size: 12px; margin: 3px; font-family: monospace;
  }

  /* Framing boxes */
  .framing-left   { background: #0D1A2E; border: 1px solid #1A2E4E; border-radius: 10px; padding: 16px 18px; }
  .framing-center { background: #0D1E18; border: 1px solid #1A3A28; border-radius: 10px; padding: 16px 18px; }
  .framing-right  { background: #2E0D0D; border: 1px solid #4E1A1A; border-radius: 10px; padding: 16px 18px; }

  /* Tab style override */
  .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #0D111C; border-radius: 10px; padding: 6px; }
  .stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 8px; color: #64748B;
    font-family: 'Inter', sans-serif; font-weight: 600; font-size: 13px;
  }
  .stTabs [aria-selected="true"] { background: #1E293B !important; color: #F1F5FB !important; }

  /* Input */
  .stTextArea textarea {
    background: #0D111C !important; border: 1px solid #1E293B !important;
    color: #E8EDF5 !important; font-size: 15px !important;
    border-radius: 10px !important;
  }
  .stTextInput input {
    background: #0D111C !important; border: 1px solid #1E293B !important;
    color: #E8EDF5 !important; border-radius: 8px !important;
  }

  /* Button */
  .stButton > button {
    background: linear-gradient(135deg, #2463EB, #1D4ED8) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 28px !important; font-size: 14px !important;
    letter-spacing: 0.5px !important;
  }
  .stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px); }

  /* History item */
  .history-item {
    background: #0D111C; border: 1px solid #1E293B; border-radius: 8px;
    padding: 12px 14px; margin-bottom: 8px; cursor: pointer;
    transition: border-color 0.2s;
  }
  .history-item:hover { border-color: #2463EB; }

  /* Spinner text */
  .analyzing-text {
    text-align: center; color: #2463EB;
    font-family: 'Inter', sans-serif; font-size: 14px;
    letter-spacing: 2px; text-transform: uppercase; padding: 20px;
  }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tsn-header">
  <div class="tsn-logo">⚖️</div>
  <div>
    <div class="tsn-title">TwoSidedNews</div>
    <div class="tsn-tagline">See Every Side. Form Your Own Truth.</div>
  </div>
</div>
<hr class="tsn-divider">
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result  = None
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ─── CLAUDE API ───────────────────────────────────────────────────────────────
def analyze_with_claude(text: str) -> dict:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    prompt = f"""You are a senior political media analyst for TwoSidedNews. Analyze the news text below.
Return ONLY a valid JSON object — no markdown, no extra text.

NEWS TEXT:
\"\"\"{text}\"\"\"

Return EXACTLY this JSON structure:
{{
  "headline_summary": "One neutral sentence summarizing the story",
  "sentiment": {{"positive": 0.0, "negative": 0.0, "neutral": 0.0}},
  "bias_score": 0.0,
  "bias_label": "left|center|right",
  "dominant_emotion": "anger|fear|joy|sadness|disgust|surprise|neutral",
  "emotions": {{"anger": 0.0, "fear": 0.0, "joy": 0.0, "sadness": 0.0, "disgust": 0.0, "surprise": 0.0, "neutral": 0.0}},
  "loaded_words": ["word1", "word2"],
  "rhetorical_devices": ["device1"],
  "left_framing": "2 sentences: how left-leaning outlets would frame this",
  "center_framing": "2 sentences: neutral, facts-only framing",
  "right_framing": "2 sentences: how right-leaning outlets would frame this",
  "flotation": {{"left_pct": 33, "center_pct": 34, "right_pct": 33}},
  "credibility_score": 72,
  "manipulation_risk": "low|medium|high",
  "manipulation_tactics": ["tactic1"],
  "key_missing_context": "One sentence on what important context is missing",
  "key_facts": ["fact1", "fact2"],
  "counterarguments": ["argument1", "argument2"],
  "urgency_language": false,
  "fear_appeal": false,
  "social_proof_used": false,
  "topic_tags": ["Politics"],
  "reading_level": "elementary|middle|high|college|expert",
  "ai_confidence": 0.85
}}

Rules:
- sentiment values must sum to 1.0
- emotions values must sum to 1.0
- bias_score: -1.0 (far left) to +1.0 (far right)
- flotation percentages must sum to 100
- credibility_score: integer 0-100
- Be precise, balanced, analytical"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ─── CHART HELPERS ────────────────────────────────────────────────────────────
def sentiment_chart(sentiment: dict):
    labels = ["Positive", "Negative", "Neutral"]
    values = [
        sentiment.get("positive", 0) * 100,
        sentiment.get("negative", 0) * 100,
        sentiment.get("neutral",  0) * 100
    ]
    colors = ["#059669", "#DC2626", "#64748B"]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors,
        text=[f"{v:.0f}%" for v in values], textposition="outside",
        textfont=dict(color="#E8EDF5", size=13, family="Inter"),
    ))
    fig.update_layout(
        paper_bgcolor="#0D111C", plot_bgcolor="#0D111C",
        font=dict(color="#94A3B8", family="Inter"),
        yaxis=dict(range=[0, 110], gridcolor="#1E293B", ticksuffix="%"),
        xaxis=dict(gridcolor="#1E293B"),
        margin=dict(t=20, b=10, l=10, r=10), height=260,
        showlegend=False,
    )
    return fig


def bias_gauge(score: float):
    score = max(-1.0, min(1.0, score))
    needle_x = (score + 1) / 2   # 0 to 1
    col = "#2463EB" if score < -0.3 else "#DC2626" if score > 0.3 else "#059669"

    fig = go.Figure()
    # Background bar
    fig.add_trace(go.Bar(
        x=["LEFT", "CENTER", "RIGHT"],
        y=[33, 34, 33],
        marker_color=["#2463EB", "#059669", "#DC2626"],
        marker_opacity=0.35,
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.update_layout(
        paper_bgcolor="#0D111C", plot_bgcolor="#0D111C",
        font=dict(color="#94A3B8", family="Inter"),
        xaxis=dict(gridcolor="#1E293B"),
        yaxis=dict(visible=False),
        margin=dict(t=10, b=10, l=10, r=10), height=160,
        annotations=[dict(
            x=needle_x, y=0.5, xref="paper", yref="paper",
            text=f"<b>{score:+.2f}</b>",
            font=dict(color=col, size=22, family="Playfair Display"),
            showarrow=True, arrowhead=2, arrowcolor=col,
            ax=0, ay=-40,
        )]
    )
    return fig


def flotation_chart(flotation: dict):
    left   = flotation.get("left_pct",   33)
    center = flotation.get("center_pct", 34)
    right  = flotation.get("right_pct",  33)
    fig = go.Figure(go.Bar(
        x=[left, center, right],
        y=["Left Media", "Center/Neutral", "Right Media"],
        orientation="h",
        marker_color=["#2463EB", "#059669", "#DC2626"],
        text=[f"{left}%", f"{center}%", f"{right}%"],
        textposition="inside",
        textfont=dict(color="white", size=13, family="Inter"),
    ))
    fig.update_layout(
        paper_bgcolor="#0D111C", plot_bgcolor="#0D111C",
        font=dict(color="#94A3B8", family="Inter"),
        xaxis=dict(range=[0, 100], gridcolor="#1E293B", ticksuffix="%"),
        yaxis=dict(gridcolor="#1E293B"),
        margin=dict(t=10, b=10, l=10, r=10), height=180,
        showlegend=False,
    )
    return fig


def emotion_radar(emotions: dict):
    emos = list(emotions.keys())
    vals = [emotions[e] * 100 for e in emos]
    vals.append(vals[0])  # close the radar
    emos.append(emos[0])
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=emos, fill="toself",
        line_color="#7C3AED",
        fillcolor="rgba(124,58,237,0.2)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#0D111C",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1E293B", color="#64748B"),
            angularaxis=dict(gridcolor="#1E293B", color="#94A3B8"),
        ),
        paper_bgcolor="#0D111C",
        font=dict(color="#94A3B8", family="Inter"),
        margin=dict(t=20, b=20, l=20, r=20), height=280,
        showlegend=False,
    )
    return fig


def credibility_gauge(score: int):
    col = "#059669" if score > 65 else "#F59E0B" if score > 35 else "#EF4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#64748B"),
            bar=dict(color=col),
            bgcolor="#1E293B",
            steps=[
                dict(range=[0, 35],  color="#2A0D0D"),
                dict(range=[35, 65], color="#2A1E0D"),
                dict(range=[65, 100],color="#0D2A1E"),
            ],
            threshold=dict(line=dict(color=col, width=3), thickness=0.75, value=score)
        ),
        number=dict(font=dict(color=col, size=36, family="Playfair Display")),
    ))
    fig.update_layout(
        paper_bgcolor="#0D111C",
        font=dict(color="#94A3B8", family="Inter"),
        margin=dict(t=20, b=10, l=20, r=20), height=220,
    )
    return fig


# ─── RENDER RESULTS ───────────────────────────────────────────────────────────
def render_results(r: dict):

    # ── Row 1: Summary + tags ──────────────────────────────────────────────
    st.markdown(f"""
    <div class="card card-amber">
      <div class="section-tag tag-amber">📰 Story Summary</div>
      <p style="font-size:16px; line-height:1.7; color:#CBD5E1; margin:0 0 12px 0;">
        {r.get('headline_summary','')}
      </p>
      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
        {''.join(f'<span style="background:#1E293B;border:1px solid #334155;border-radius:20px;padding:3px 12px;font-size:11px;color:#94A3B8;">{t}</span>' for t in r.get('topic_tags', []))}
        <span style="background:#1E293B;border:1px solid #334155;border-radius:20px;padding:3px 12px;font-size:11px;color:#94A3B8;">
          📚 {r.get('reading_level','').upper()} LEVEL
        </span>
        <span class="risk-{r.get('manipulation_risk','low')}">
          ⚡ {r.get('manipulation_risk','').upper()} MANIPULATION RISK
        </span>
        <span style="background:#1E1A2A;border:1px solid #2E2A3A;border-radius:20px;padding:3px 12px;font-size:11px;color:#7C3AED;">
          AI Confidence: {int(r.get('ai_confidence',0)*100)}%
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 2: Sentiment | Bias | Credibility ──────────────────────────────
    col1, col2, col3 = st.columns([1.1, 1.1, 0.9])

    with col1:
        st.markdown('<div class="section-tag tag-green" style="margin-bottom:4px;">SENTIMENT BREAKDOWN</div>', unsafe_allow_html=True)
        st.plotly_chart(sentiment_chart(r.get("sentiment", {})), use_container_width=True, config={"displayModeBar": False})

    with col2:
        bias_score = r.get("bias_score", 0)
        bias_label = r.get("bias_label", "center")
        col_map = {"left": "#2463EB", "center": "#059669", "right": "#DC2626"}
        bcol = col_map.get(bias_label, "#059669")
        st.markdown('<div class="section-tag tag-blue" style="margin-bottom:4px;">POLITICAL LEAN</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0D111C;border:1px solid #1E293B;border-radius:10px;padding:18px;text-align:center;">
          <div style="font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:900;color:{bcol};">
            {bias_label.upper()}
          </div>
          <div style="font-size:1.1rem;color:{bcol};font-family:monospace;margin:4px 0 12px;">
            Score: {bias_score:+.2f}
          </div>
          <div style="height:10px;border-radius:5px;background:linear-gradient(to right,#1D4ED8,#059669,#DC2626);position:relative;">
            <div style="position:absolute;top:-4px;left:{int((bias_score+1)/2*100)}%;transform:translateX(-50%);
              width:18px;height:18px;border-radius:50%;background:#fff;border:3px solid {bcol};
              box-shadow:0 0 8px {bcol}66;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:10px;color:#64748B;">
            <span>← LEFT</span><span>CENTER</span><span>RIGHT →</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="section-tag tag-amber" style="margin-bottom:4px;">CREDIBILITY SCORE</div>', unsafe_allow_html=True)
        st.plotly_chart(credibility_gauge(r.get("credibility_score", 50)), use_container_width=True, config={"displayModeBar": False})

    # ── Row 3: Flotation ───────────────────────────────────────────────────
    st.markdown('<div class="section-tag tag-green" style="margin:8px 0 4px;">WEB FLOTATION — ESTIMATED MEDIA COVERAGE DISTRIBUTION</div>', unsafe_allow_html=True)
    st.plotly_chart(flotation_chart(r.get("flotation", {})), use_container_width=True, config={"displayModeBar": False})

    # ── Row 4: Emotion radar + persuasion signals ──────────────────────────
    col4, col5 = st.columns(2)

    with col4:
        st.markdown('<div class="section-tag tag-purple" style="margin-bottom:4px;">EMOTION PROFILE</div>', unsafe_allow_html=True)
        st.plotly_chart(emotion_radar(r.get("emotions", {})), use_container_width=True, config={"displayModeBar": False})

    with col5:
        st.markdown('<div class="section-tag tag-red" style="margin-bottom:4px;">PERSUASION SIGNALS</div>', unsafe_allow_html=True)
        signals = [
            ("Urgency Language",   r.get("urgency_language",   False)),
            ("Fear Appeal",        r.get("fear_appeal",        False)),
            ("Social Proof Used",  r.get("social_proof_used",  False)),
        ]
        for label, val in signals:
            color = "#EF4444" if val else "#059669"
            icon  = "🔴 DETECTED" if val else "🟢 NOT FOUND"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
              padding:10px 14px;background:#0D111C;border:1px solid #1E293B;
              border-radius:8px;margin-bottom:8px;">
              <span style="font-size:13px;color:#94A3B8;">{label}</span>
              <span style="font-size:11px;font-weight:700;color:{color};
                background:{color}22;border:1px solid {color}44;
                border-radius:4px;padding:2px 8px;">{icon}</span>
            </div>
            """, unsafe_allow_html=True)

        # Loaded words
        if r.get("loaded_words"):
            st.markdown('<div class="section-tag tag-amber" style="margin:12px 0 6px;">LOADED WORDS</div>', unsafe_allow_html=True)
            words_html = " ".join(f'<span class="word-tag">"{w}"</span>' for w in r["loaded_words"])
            st.markdown(f"<div>{words_html}</div>", unsafe_allow_html=True)

        if r.get("rhetorical_devices"):
            st.markdown('<div class="section-tag tag-purple" style="margin:12px 0 6px;">RHETORICAL DEVICES</div>', unsafe_allow_html=True)
            devs_html = " ".join(f'<span style="display:inline-block;background:#1A0D2A;border:1px solid #2E1A4A;color:#A78BFA;padding:3px 10px;border-radius:6px;font-size:12px;margin:3px;">{d}</span>' for d in r["rhetorical_devices"])
            st.markdown(f"<div>{devs_html}</div>", unsafe_allow_html=True)

    # ── Row 5: Three framings ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-tag tag-blue" style="margin-bottom:12px;">THREE PERSPECTIVES — SAME STORY, DIFFERENT LENS</div>', unsafe_allow_html=True)

    cf1, cf2, cf3 = st.columns(3)
    with cf1:
        st.markdown(f"""
        <div class="framing-left">
          <div class="section-tag tag-blue">← LEFT FRAMING</div>
          <p style="font-size:13.5px;line-height:1.7;color:#93C5FD;margin:0;">{r.get('left_framing','')}</p>
        </div>""", unsafe_allow_html=True)
    with cf2:
        st.markdown(f"""
        <div class="framing-center">
          <div class="section-tag tag-green">◉ CENTER / NEUTRAL</div>
          <p style="font-size:13.5px;line-height:1.7;color:#6EE7B7;margin:0;">{r.get('center_framing','')}</p>
        </div>""", unsafe_allow_html=True)
    with cf3:
        st.markdown(f"""
        <div class="framing-right">
          <div class="section-tag tag-red">RIGHT FRAMING →</div>
          <p style="font-size:13.5px;line-height:1.7;color:#FCA5A5;margin:0;">{r.get('right_framing','')}</p>
        </div>""", unsafe_allow_html=True)

    # ── Row 6: Key Facts | Counterarguments | Missing Context ─────────────
    st.markdown("---")
    ck1, ck2, ck3 = st.columns(3)

    with ck1:
        st.markdown('<div class="card card-center"><div class="section-tag tag-green">✓ KEY FACTS STATED</div>', unsafe_allow_html=True)
        for f in r.get("key_facts", []):
            st.markdown(f"<p style='font-size:12.5px;color:#CBD5E1;margin:4px 0;'>✓ {f}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with ck2:
        st.markdown('<div class="card card-amber"><div class="section-tag tag-amber">↔ COUNTERARGUMENTS</div>', unsafe_allow_html=True)
        for c in r.get("counterarguments", []):
            st.markdown(f"<p style='font-size:12.5px;color:#CBD5E1;margin:4px 0;'>↔ {c}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with ck3:
        st.markdown(f"""
        <div class="card card-right">
          <div class="section-tag tag-amber">⚠ MISSING CONTEXT</div>
          <p style="font-size:13px;line-height:1.6;color:#C8B87A;margin:0;">{r.get('key_missing_context','')}</p>
        </div>""", unsafe_allow_html=True)


# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["⚖️  Analyze", "🔄  Compare Two Articles", "📁  History"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALYZE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <p style="color:#64748B;font-size:14px;margin-bottom:16px;">
    Paste any news headline, paragraph, or full article. The AI will analyze sentiment,
    political bias, credibility, emotional tone, and show you how Left, Center, and
    Right media would frame the same story.
    </p>
    """, unsafe_allow_html=True)

    input_text = st.text_area(
        "News Text",
        placeholder="Paste any news article, headline, or paragraph here...",
        height=140,
        label_visibility="collapsed",
        key="main_input"
    )

    col_btn, col_hint, col_clear = st.columns([1.5, 4, 1])
    with col_btn:
        analyze_btn = st.button("⚖️  Analyze", use_container_width=True)
    with col_hint:
        st.markdown("<p style='color:#334155;font-size:12px;margin-top:10px;'>Powered by Claude AI · 15+ analysis dimensions</p>", unsafe_allow_html=True)
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.result = None
            st.rerun()

    if analyze_btn and input_text.strip():
        with st.spinner(""):
            st.markdown('<div class="analyzing-text">ANALYZING · DETECTING BIAS · MAPPING PERSPECTIVES...</div>', unsafe_allow_html=True)
            try:
                result = analyze_with_claude(input_text.strip())
                st.session_state.result = result
                st.session_state.history.insert(0, {
                    "text":      input_text.strip()[:200],
                    "result":    result,
                    "timestamp": datetime.now().strftime("%H:%M · %d %b")
                })
                if len(st.session_state.history) > 15:
                    st.session_state.history = st.session_state.history[:15]
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    elif analyze_btn:
        st.warning("Please paste some news text first.")

    if st.session_state.result:
        st.markdown("---")
        render_results(st.session_state.result)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <p style="color:#64748B;font-size:14px;margin-bottom:16px;">
    Paste two different articles covering the same story — from different outlets or different
    perspectives — and compare their bias, sentiment, and framing side-by-side.
    </p>
    """, unsafe_allow_html=True)

    cca, ccb = st.columns(2)
    with cca:
        st.markdown('<div class="section-tag tag-blue">ARTICLE A</div>', unsafe_allow_html=True)
        text_a = st.text_area("Article A", placeholder="Paste first article here...", height=130, label_visibility="collapsed", key="cmp_a")
    with ccb:
        st.markdown('<div class="section-tag tag-red">ARTICLE B</div>', unsafe_allow_html=True)
        text_b = st.text_area("Article B", placeholder="Paste second article here...", height=130, label_visibility="collapsed", key="cmp_b")

    compare_btn = st.button("🔄  Compare Articles", use_container_width=False)

    if compare_btn:
        if not text_a.strip() or not text_b.strip():
            st.warning("Please paste both articles.")
        else:
            with st.spinner("Analyzing both articles..."):
                try:
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as ex:
                        fa_future = ex.submit(analyze_with_claude, text_a.strip())
                        fb_future = ex.submit(analyze_with_claude, text_b.strip())
                        res_a = fa_future.result()
                        res_b = fb_future.result()

                    st.markdown("---")
                    st.markdown('<div class="section-tag tag-blue" style="margin-bottom:16px;">SIDE-BY-SIDE COMPARISON</div>', unsafe_allow_html=True)

                    col_a, col_b = st.columns(2)

                    for col, res, label, col_tag, card_class in [
                        (col_a, res_a, "ARTICLE A", "tag-blue",  "card-left"),
                        (col_b, res_b, "ARTICLE B", "tag-red",   "card-right"),
                    ]:
                        with col:
                            bs = res.get("bias_score", 0)
                            bl = res.get("bias_label", "center")
                            bcol = {"left":"#2463EB","center":"#059669","right":"#DC2626"}.get(bl,"#059669")
                            st.markdown(f"""
                            <div class="card {card_class}">
                              <div class="section-tag {col_tag}">{label}</div>
                              <p style="font-size:13px;color:#94A3B8;margin:0 0 12px;">{res.get('headline_summary','')}</p>
                              <div style="margin-bottom:10px;">
                                <span style="font-size:1.6rem;font-weight:900;color:{bcol};font-family:'Playfair Display',serif;">
                                  {bl.upper()}
                                </span>
                                <span style="font-size:13px;color:{bcol};font-family:monospace;margin-left:8px;">{bs:+.2f}</span>
                              </div>
                              <div style="display:flex;gap:8px;flex-wrap:wrap;">
                                <span class="risk-{res.get('manipulation_risk','low')}">{res.get('manipulation_risk','').upper()} RISK</span>
                                <span style="background:#1E293B;border:1px solid #334155;border-radius:20px;padding:3px 12px;font-size:11px;color:#94A3B8;">
                                  CRED: {res.get('credibility_score',0)}/100
                                </span>
                              </div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.plotly_chart(sentiment_chart(res.get("sentiment",{})), use_container_width=True, config={"displayModeBar":False})
                            st.plotly_chart(flotation_chart(res.get("flotation",{})), use_container_width=True, config={"displayModeBar":False})

                    # Diff metrics
                    st.markdown("---")
                    st.markdown('<div class="section-tag tag-amber" style="margin-bottom:12px;">HEAD-TO-HEAD DIFFERENCE</div>', unsafe_allow_html=True)
                    dm1, dm2, dm3 = st.columns(3)
                    bias_diff  = abs(res_a.get("bias_score",0) - res_b.get("bias_score",0))
                    cred_diff  = abs(res_a.get("credibility_score",0) - res_b.get("credibility_score",0))
                    neg_diff   = abs((res_a.get("sentiment",{}).get("negative",0) - res_b.get("sentiment",{}).get("negative",0)) * 100)

                    for col, val, unit, label in [
                        (dm1, f"{bias_diff:.2f}", "pts", "Bias Gap"),
                        (dm2, str(cred_diff),      "pts", "Credibility Gap"),
                        (dm3, f"{neg_diff:.0f}",  "%",   "Negativity Δ"),
                    ]:
                        with col:
                            st.markdown(f"""
                            <div style="background:#0D111C;border:1px solid #1E293B;border-radius:10px;
                              padding:16px;text-align:center;">
                              <div class="big-stat" style="color:#F1F5FB;">{val}<span style="font-size:1rem;color:#64748B;">{unit}</span></div>
                              <div class="stat-label">{label}</div>
                            </div>
                            """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Comparison failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state.history:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#334155;">
          <div style="font-size:3rem;margin-bottom:12px;">📰</div>
          <div style="font-family:monospace;letter-spacing:2px;text-transform:uppercase;">No analyses yet</div>
          <div style="font-size:13px;margin-top:8px;color:#1E293B;">Go to Analyze tab to get started</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        h_col1, h_col2 = st.columns([4, 1])
        with h_col2:
            if st.button("🗑  Clear All"):
                st.session_state.history = []
                st.rerun()

        for i, item in enumerate(st.session_state.history):
            r = item["result"]
            bs = r.get("bias_score", 0)
            bl = r.get("bias_label", "center")
            bcol = {"left":"#2463EB","center":"#059669","right":"#DC2626"}.get(bl,"#059669")

            with st.expander(f"📰  {item['text'][:80]}...  ·  {item['timestamp']}", expanded=False):
                st.markdown(f"""
                <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;">
                  <span style="font-size:14px;font-weight:700;color:{bcol};">{bl.upper()} ({bs:+.2f})</span>
                  <span class="risk-{r.get('manipulation_risk','low')}">{r.get('manipulation_risk','').upper()} RISK</span>
                  <span style="background:#1E293B;border:1px solid #334155;border-radius:20px;padding:3px 12px;font-size:11px;color:#94A3B8;">
                    CREDIBILITY: {r.get('credibility_score',0)}/100
                  </span>
                </div>
                <p style="font-size:13px;color:#94A3B8;">{r.get('headline_summary','')}</p>
                """, unsafe_allow_html=True)

                col_l, col_c, col_r = st.columns(3)
                with col_l:
                    st.markdown(f'<div class="framing-left"><div class="section-tag tag-blue">← LEFT</div><p style="font-size:12px;color:#93C5FD;margin:0;">{r.get("left_framing","")}</p></div>', unsafe_allow_html=True)
                with col_c:
                    st.markdown(f'<div class="framing-center"><div class="section-tag tag-green">◉ CENTER</div><p style="font-size:12px;color:#6EE7B7;margin:0;">{r.get("center_framing","")}</p></div>', unsafe_allow_html=True)
                with col_r:
                    st.markdown(f'<div class="framing-right"><div class="section-tag tag-red">RIGHT →</div><p style="font-size:12px;color:#FCA5A5;margin:0;">{r.get("right_framing","")}</p></div>', unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#1E293B;margin:40px 0 16px;">
<div style="text-align:center;font-family:monospace;font-size:10px;color:#1E293B;letter-spacing:2px;">
  TWOSIDEDNEWS · POWERED BY CLAUDE AI · SEE EVERY SIDE · FORM YOUR OWN TRUTH
</div>
""", unsafe_allow_html=True)
