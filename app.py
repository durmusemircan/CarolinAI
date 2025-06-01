import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# --- DATEN LADEN ---
produkt_df = pd.read_pickle('produkt_uebersicht.pkl')
df = pd.read_pickle('alle_kommentare.pkl')

st.set_page_config(page_title="Produktbewertungsanalyse", layout="wide")

# ---- MODERN PASTELL DESIGN ----
st.markdown("""
<style>
body, .main {
    background: linear-gradient(120deg,#e3ecfc 0%,#fafcff 100%) !important;
}
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.80);
    border: 1px solid #e0e6ef;
    border-radius: 19px;
    padding: 16px;
    margin: 12px 2px 12px 2px;
    box-shadow: 0 2px 24px 0 rgba(34,45,67,0.09);
}
div[data-testid="stMetricValue"] {
    color: #1877F2;
    font-weight: 900;
}
</style>
""", unsafe_allow_html=True)

st.title("👶 Produktbasierte KI-Bewertungsanalyse – Marktübersicht & Vergleich")

# --- GESAMTANALYSE BERECHNEN ---
gesamt_ai = round(100 * len(df[df['sentiment_label']=='positive']) / len(df),2)
gesamt_user = round(100 * len(df[df['rating_sentiment']=='positiv']) / len(df),2)
gesamt_ø = round(df['Bewertung'].mean(),2)

col1, col2, col3 = st.columns(3)
col1.metric("🤖 Gesamt Zufriedenheit Kommentare", f"{gesamt_ai} %")
col2.metric("👥 Gesamt Zufriedenheit Sterne", f"{gesamt_user} %")
col3.metric("⭐ Durchschnittsbewertung", gesamt_ø)

# --- GESAMTE SENTIMENT-VERTEILUNG ---
st.markdown("#### 📊 Gesamte KI-Sentiment-Verteilung")
sentiment_counts = df['sentiment_label'].value_counts()
sentiment_labels = {'positive':'Positiv', 'neutral':'Neutral', 'negative':'Negativ'}
bar_colors = ['#65e4a3', '#c1f1fd', '#f76c6c']

fig_sent = px.bar(
    x=[sentiment_labels.get(s,s) for s in sentiment_counts.index],
    y=sentiment_counts.values,
    color=[sentiment_labels.get(s,s) for s in sentiment_counts.index],
    color_discrete_sequence=bar_colors,
    labels={'x':'Sentiment', 'y':'Anzahl'},
    text_auto=True,
)
fig_sent.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(gridcolor='#e0e0e0'),
    showlegend=False,
    height=340
)
st.plotly_chart(fig_sent, use_container_width=True)

st.markdown("---")

# --- RANKINGS ---
st.markdown("### 🏆 Produkt-Rankings & Vergleich")
tabs = st.tabs(["🥇 Nach Zufriedenheit Kommentare", "💬 Nach Zufriedenheit Sterne", "⭐ Nach Durchschnittsbewertung"])

with tabs[0]:
    st.subheader("Produkte mit höchstem Zufriedenheit Kommentare")
    st.dataframe(
        produkt_df[["Produkt", "Zufriedenheit Kommentare (%)", "Anzahl Bewertungen"]].sort_values("Zufriedenheit Kommentare (%)", ascending=False).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

with tabs[1]:
    st.subheader("Produkte mit höchstem Zufriedenheit Sterne")
    st.dataframe(
        produkt_df[["Produkt", "Zufriedenheit Sterne (%)", "Anzahl Bewertungen"]].sort_values("Zufriedenheit Sterne (%)", ascending=False).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

with tabs[2]:
    st.subheader("Produkte mit höchster Durchschnittsbewertung")
    st.dataframe(
        produkt_df[["Produkt", "Ø Bewertung", "Anzahl Bewertungen"]].sort_values("Ø Bewertung", ascending=False).reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# --- EINZELPRODUKT-ANALYSE ---
st.markdown("<h3 style='color:#1565c0; font-weight:700'>🔍 Einzelprodukt-Analyse</h3>", unsafe_allow_html=True)
auswahl = produkt_df["Produkt"].tolist()
ausgewaehlt = st.selectbox("Wähle ein Produkt für Details:", auswahl)

row = produkt_df[produkt_df['Produkt'] == ausgewaehlt].iloc[0]

# KARTEN FÜR EINZELPRODUKT
st.markdown(
    f"""
    <div style="display: flex; gap: 20px;">
        <div style="flex:1; background:#e0f9e7bb; border-radius:14px; padding:14px 18px; margin-bottom:8px; box-shadow:0 2px 10px #d0e2e5;">
            <b style="color:#28a745; font-size:1.07em;">💚 Positivster Kommentar:</b>
            <div style="margin-top:8px; color:#212529;">{row['Positivster Kommentar']}</div>
        </div>
        <div style="flex:1; background:#ffe0e6bb; border-radius:14px; padding:14px 18px; margin-bottom:8px; box-shadow:0 2px 10px #f8d7da;">
            <b style="color:#d6336c; font-size:1.07em;">💔 Negativster Kommentar:</b>
            <div style="margin-top:8px; color:#212529;">{row['Negativster Kommentar']}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
c1.metric("Anzahl Bewertungen", row["Anzahl Bewertungen"])
c2.metric("Zufriedenheit Kommentare (%)", row["Zufriedenheit Kommentare (%)"])
c3.metric("Ø Bewertung", row["Ø Bewertung"])

st.markdown("---")

# --- EINZELPRODUKT ALLE KOMMENTARE ---
with st.expander("📑 Alle Kommentare für dieses Produkt anzeigen"):
    alle_kommentare = df[df['Artikel'] == ausgewaehlt][
        ['Bewertungstext', 'Bewertung', 'sentiment_label', 'sentiment_score']
    ].rename(
        columns={
            'Bewertungstext': 'Kommentar',
            'Bewertung': 'Punktzahl',
            'sentiment_label': 'KI-Sentiment',
            'sentiment_score': 'KI-Score'
        }
    )
    st.dataframe(
        alle_kommentare.style
        .bar(subset=["KI-Score"], color=["#a7f0ba", "#fdfdcf"], vmin=0, vmax=1)
        .format({'KI-Score': '{:.2f}'}),
        use_container_width=True
    )

st.markdown(
    "<div style='text-align:center; color:#a7adbd; font-size:0.92em; margin-top:30px;'>"
    "Carolin Nowak| Powered by Emircan Durmus"
    "</div>", unsafe_allow_html=True
)
