import streamlit as st
import yfinance as yf
import pandas as pd
import random

# Configuration de la page
st.set_page_config(
    page_title="Trading Quest PRO ⚡",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS SUR-MESURE ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,255,150,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- TRADUCTIONS (FR / EN) ---
TEXTS = {
    "FR": {
        "title": "⚡ TRADING QUEST PRO",
        "subtitle": "Terminal de simulation boursière & Gestion de portefeuille",
        "level": "Niveau",
        "xp": "XP",
        "ranks": {1: "🟢 Novice des Marchés", 2: "🔵 Trader Averti", 3: "🟣 Analyste Senior", 4: "👑 Loup de Wall Street"},
        "high_rank": "🔥 Demi-Dieu de la Finance",
        "cash": "Cash disponible",
        "portfolio_val": "Portefeuille Actions",
        "total_net": "Patrimoine Net",
        "chest_title": "🎁 Bonus Quotidien & Récompenses",
        "chest_btn": "⚡ RÉCLAMER LE BONUS QUOTIDIEN 🔮",
        "chest_success": "🎉 INCROYABLE ! Tu as reçu un bonus de **+{gain} $** et **+30 XP** !",
        "chest_claimed": "✅ Récompense du jour déjà réclamée !",
        "tabs": ["📈 Trading Desk", "🏛️ Comparatif Marché", "📊 Vues & Tendances 7J", "🏆 Bilan & Stats"],
        "select_company": "Sélectionner un actif :",
        "quantity": "Quantité de titres :",
        "buy_btn": "🚀 ACHETER POUR {cost:,.2f} $",
        "sell_btn": "💸 VENDRE POUR {revenue:,.2f} $",
        "buy_success": "💥 ACHAT VALIDÉ ! {qty} x {sym} pour {cost:,.2f} $. (+{xp} XP)",
        "sell_success": "💰 VENTE VALIDÉE ! {qty} x {sym} pour {revenue:,.2f} $. (+{xp} XP)",
        "no_funds": "❌ Fonds insuffisants pour exécuter cet ordre.",
        "no_shares": "❌ Position insuffisante pour vendre cette quantité.",
        "error_fetch": "Erreur d'accès aux données du marché.",
        "my_portfolio": "💼 Vos Positions Actives",
        "no_stocks": "Aucune position ouverte.",
        "shares": "titre(s)",
        "summary_title": "📋 Indicateurs Clefs",
        "prev_close": "Clôture Précédente",
        "day_high": "Plus Haut (24h)",
        "day_low": "Plus Bas (24h)",
        "volume": "Volume 24h",
        "leaderboard_title": "🏆 Profil & Statistiques Globales",
        "weekly_summary": "📅 Tendances de la Semaine",
        "comparison_title": "🏛️ Comparatif des Grandes Valeurs",
        "setup_title": "⚡ Bienvenue sur Trading Quest",
        "setup_sub": "Initialisez votre terminal de trading professionnel.",
        "username_prompt": "Identifiant / Pseudo Trader :",
        "start_btn": "🚀 Lancer le Terminal",
        "logout_btn": "🚪 Déconnexion",
        "refresh_btn": "🔄 Actualiser les cours",
        "welcome": "Session Active"
    },
    "EN": {
        "title": "⚡ TRADING QUEST PRO",
        "subtitle": "Trading Simulation Terminal & Portfolio Manager",
        "level": "Level",
        "xp": "XP",
        "ranks": {1: "🟢 Market Novice", 2: "🔵 Savvy Trader", 3: "🟣 Senior Analyst", 4: "👑 Wall Street Wolf"},
        "high_rank": "🔥 Financial Demigod",
        "cash": "Available Cash",
        "portfolio_val": "Portfolio Value",
        "total_net": "Total Net Worth",
        "chest_title": "🎁 Daily Rewards & Chest",
        "chest_btn": "⚡ CLAIM DAILY BONUS 🔮",
        "chest_success": "🎉 AWESOME! Bonus claimed: **+${gain}** and **+30 XP**!",
        "chest_claimed": "✅ Daily reward already claimed!",
        "tabs": ["📈 Trading Desk", "🏛️ Market Overview", "📊 7-Day Trends", "🏆 Profile & Stats"],
        "select_company": "Select Asset:",
        "quantity": "Share Quantity:",
        "buy_btn": "🚀 BUY FOR ${cost:,.2f}",
        "sell_btn": "💸 SELL FOR ${revenue:,.2f}",
        "buy_success": "💥 ORDER FILLED! {qty} x {sym} for ${cost:,.2f}. (+{xp} XP)",
        "sell_success": "💰 POSITION CLOSED! {qty} x {sym} for ${revenue:,.2f}. (+{xp} XP)",
        "no_funds": "❌ Insufficient cash to execute order.",
        "no_shares": "❌ Insufficient shares to sell.",
        "error_fetch": "Error fetching market data.",
        "my_portfolio": "💼 Active Positions",
        "no_stocks": "No open positions.",
        "shares": "share(s)",
        "summary_title": "📋 Key Metrics",
        "prev_close": "Prev Close",
        "day_high": "Day High",
        "day_low": "Day Low",
        "volume": "Volume",
        "leaderboard_title": "🏆 Account Overview & Performance",
        "weekly_summary": "📅 Weekly Market Overview",
        "comparison_title": "🏛️ Market Giants Comparison",
        "setup_title": "⚡ Welcome to Trading Quest",
        "setup_sub": "Initialize your professional trading terminal.",
        "username_prompt": "Trader Handle / Username:",
        "start_btn": "🚀 Launch Terminal",
        "logout_btn": "🚪 Logout",
        "refresh_btn": "🔄 Refresh Market Data",
        "welcome": "Active Session"
    }
}

# --- MENU LATÉRAL ---
st.sidebar.title("☰ Terminal Options")
langue = st.sidebar.selectbox("🌐 Langue / Language", ["FR 🇫🇷", "EN 🇬🇧"])
lang_code = "FR" if "FR" in langue else "EN"
t = TEXTS[lang_code]

# Bouton de rafraîchissement manuel
if st.sidebar.button(t["refresh_btn"], use_container_width=True):
    st.rerun()

# --- INITIALISATION DE SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "solde" not in st.session_state:
    st.session_state.solde = 1000.0
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "portefeuille" not in st.session_state:
    st.session_state.portefeuille = {}
if "bonus_reclame" not in st.session_state:
    st.session_state.bonus_reclame = False

# --- PAGE D'ACCUEIL / SETUP INITIAL ---
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    c_left, c_mid, c_right = st.columns([1, 2, 1])
    with c_mid:
        st.title(t["setup_title"])
        st.caption(t["setup_sub"])
        st.divider()
        username_input = st.text_input(t["username_prompt"], value="Youssef")
        if st.button(t["start_btn"], use_container_width=True, type="primary"):
            if username_input.strip():
                st.session_state.username = username_input.strip()
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# Bouton de déconnexion dans le menu
st.sidebar.divider()
if st.sidebar.button(t["logout_btn"], use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# --- CALCUL DU NIVEAU & ASSETS ---
niveau = (st.session_state.xp // 100) + 1
rang = t["ranks"].get(niveau, t["high_rank"])

MARQUES = {
    "Apple Inc.": "AAPL",
    "Microsoft Corp.": "MSFT",
    "NVIDIA Corp.": "NVDA",
    "Alphabet Inc. (Google)": "GOOGL",
    "Amazon.com Inc.": "AMZN",
    "Tesla Inc.": "TSLA",
    "Meta Platforms": "META",
    "iShares Bitcoin ETF": "IBIT"
}

# --- HEADER PRINCIPAL ---
st.title(t["title"])
st.caption(f"{t['subtitle']} | **{t['welcome']} :** `{st.session_state.username}`")

# Barre de niveau & progression
col_lvl, col_xp = st.columns([1, 3])
with col_lvl:
    st.subheader(f"{t['level']} {niveau}")
    st.caption(rang)
with col_xp:
    progression = (st.session_state.xp % 100) / 100
    st.progress(progression, text=f"{t['xp']} : {st.session_state.xp % 100} / 100 XP")

# --- TABLEAU DE BORD FINANCIER (METRICS) ---
valeur_actions = 0.0
for sym, data in st.session_state.portefeuille.items():
    try:
        p_actuel = yf.Ticker(sym).history(period="1d")["Close"].iloc[-1]
        valeur_actions += p_actuel * data["quantite"]
    except:
        valeur_actions += data["prix_moyen"] * data["quantite"]

total_patrimoine = st.session_state.solde + valeur_actions
benefice_total = total_patrimoine - 1000.0

m1, m2, m3 = st.columns(3)
m1.metric(t["cash"], f"{st.session_state.solde:,.2f} $")
m2.metric(t["portfolio_val"], f"{valeur_actions:,.2f} $")
m3.metric(t["total_net"], f"{total_patrimoine:,.2f} $", delta=f"{benefice_total:+,.2f} $")

st.divider()

# --- RECOMPENSE QUOTIDIENNE ---
if not st.session_state.bonus_reclame:
    with st.container():
        st.subheader(t["chest_title"])
        c_chest1, c_chest2 = st.columns([1, 4])
        with c_chest1:
            st.markdown("<h2 style='text-align: center; margin: 0;'>🎁</h2>", unsafe_allow_html=True)
        with c_chest2:
            if st.button(t["chest_btn"], use_container_width=True, type="primary"):
                gain = random.choice([50, 100, 200, 500, 1000])
                st.session_state.solde += gain
                st.session_state.xp += 30
                st.session_state.bonus_reclame = True
                st.balloons()
                st.success(t["chest_success"].format(gain=gain))
                st.rerun()
    st.divider()

# --- ONGLETS INTERACTIFS ---
tab1, tab2, tab3, tab4 = st.tabs(t["tabs"])

# --- TAB 1 : TRADING DESK (ACHAT / VENTE) ---
with tab1:
    col_sel, col_empty = st.columns([2, 1])
    with col_sel:
        choix = st.selectbox(t["select_company"], list(MARQUES.keys()))
    symbole = MARQUES[choix]

    try:
        ticker = yf.Ticker(symbole)
        df_hist = ticker.history(period="1mo")
        info = ticker.fast_info
        prix_actuel = df_hist["Close"].iloc[-1]

        c_desk1, c_desk2 = st.columns([2, 1])

        with c_desk1:
            st.markdown(f"### {choix} (`{symbole}`)")
            st.markdown(f"**Prix unitaire en direct :** `{prix_actuel:,.2f} $`")
            st.line_chart(df_hist["Close"], height=280)

            # Saisie de la quantité (calcul réactif automatique à la saisie)
            quantite = st.number_input(t["quantity"], min_value=1, value=1, step=1)
            
            # CALCUL AUTOMATIQUE DE LA SOMME TOTALE
            total_val = prix_actuel * quantite

            # Affichage en direct du montant total calculé
            st.info(f"💵 **Total estimé : {total_val:,.2f} $** ({quantite} × {prix_actuel:,.2f} $)")

            btn_b, btn_s = st.columns(2)
            
            # Bouton d'achat réactif
            with btn_b:
                if st.button(t["buy_btn"].format(cost=total_val), use_container_width=True, type="primary"):
                    if total_val <= st.session_state.solde:
                        st.session_state.solde -= total_val
                        g_xp = 20 * quantite
                        st.session_state.xp += g_xp
                        if symbole in st.session_state.portefeuille:
                            st.session_state.portefeuille[symbole]["quantite"] += quantite
                        else:
                            st.session_state.portefeuille[symbole] = {"quantite": quantite, "prix_moyen": prix_actuel}
                        st.balloons()
                        st.success(t["buy_success"].format(qty=quantite, sym=symbole, cost=total_val, xp=g_xp))
                        st.rerun()
                    else:
                        st.error(t["no_funds"])

            # Bouton de vente réactif
            with btn_s:
                if st.button(t["sell_btn"].format(revenue=total_val), use_container_width=True):
                    if symbole in st.session_state.portefeuille and st.session_state.portefeuille[symbole]["quantite"] >= quantite:
                        st.session_state.solde += total_val
                        g_xp = 15 * quantite
                        st.session_state.xp += g_xp
                        st.session_state.portefeuille[symbole]["quantite"] -= quantite
                        if st.session_state.portefeuille[symbole]["quantite"] == 0:
                            del st.session_state.portefeuille[symbole]
                        st.success(t["sell_success"].format(qty=quantite, sym=symbole, revenue=total_val, xp=g_xp))
                        st.rerun()
                    else:
                        st.error(t["no_shares"])

        with c_desk2:
            st.markdown(f"#### {t['summary_title']}")
            st.metric(t["prev_close"], f"{info.get('previousClose', prix_actuel):,.2f} $")
            st.metric(t["day_high"], f"{info.get('dayHigh', prix_actuel):,.2f} $")
            st.metric(t["day_low"], f"{info.get('dayLow', prix_actuel):,.2f} $")
            st.metric(t["volume"], f"{info.get('lastVolume', 0):,}")

    except Exception:
        st.error(t["error_fetch"])

# --- TAB 2 : COMPARATIF MARCHÉ ---
with tab2:
    st.subheader(t["comparison_title"])
    comp_list = []
    for nom, sym in MARQUES.items():
        try:
            t_obj = yf.Ticker(sym)
            p = t_obj.history(period="1d")["Close"].iloc[-1]
            prev = t_obj.fast_info.get("previousClose", p)
            var = ((p - prev) / prev) * 100
            comp_list.append({"Actif": nom, "Ticker": sym, "Prix ($)": round(p, 2), "Variation 24h": f"{var:+.2f}%"})
        except:
            comp_list.append({"Actif": nom, "Ticker": sym, "Prix ($)": "N/A", "Variation 24h": "N/A"})

    st.dataframe(pd.DataFrame(comp_list), use_container_width=True)

# --- TAB 3 : TENDANCES 7J ---
with tab3:
    st.subheader(t["weekly_summary"])
    w_data = {}
    for nom, sym in list(MARQUES.items())[:5]:
        try:
            w_data[nom] = yf.Ticker(sym).history(period="7d")["Close"]
        except:
            pass
    if w_data:
        df_w = pd.DataFrame(w_data)
        st.line_chart(df_w)
        st.dataframe(df_w.style.highlight_max(axis=0), use_container_width=True)

# --- TAB 4 : STATS ---
with tab4:
    st.subheader(t["leaderboard_title"])
    stats_data = [
        {"Indicateur": "Trader Handle", "Valeur": st.session_state.username},
        {"Indicateur": "Rang Actuel", "Valeur": f"Niveau {niveau} ({rang})"},
        {"Indicateur": "Expérience (XP)", "Valeur": f"{st.session_state.xp} XP"},
        {"Indicateur": "Liquidités", "Valeur": f"{st.session_state.solde:,.2f} $"},
        {"Indicateur": "Valorisation Portefeuille", "Valeur": f"{valeur_actions:,.2f} $"},
        {"Indicateur": "Patrimoine Global", "Valeur": f"{total_patrimoine:,.2f} $"},
        {"Indicateur": "Performance Absolue", "Valeur": f"{benefice_total:+,.2f} $"}
    ]
    st.table(pd.DataFrame(stats_data))

st.divider()

# --- MES POSITIONS EN COURS ---
st.subheader(t["my_portfolio"])
if st.session_state.portefeuille:
    for sym, details in st.session_state.portefeuille.items():
        st.write(f"- **{sym}** : `{details['quantite']}` {t['shares']}")
else:
    st.info(t["no_stocks"])
