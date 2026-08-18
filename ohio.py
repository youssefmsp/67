import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Simulateur Bourse", page_icon="📈")

st.title("📈 Mon Simulateur de Bourse")
st.write("Bienvenue sur ton application ! Entraîne-toi avec du capital fictif.")

solde = 1000.0
st.metric(label="Ton solde disponible", value=f"{solde:.2f} $")

st.divider()

symbole = st.text_input("Entre le symbole d'une entreprise (ex: AAPL, TSLA, NVDA) :", "AAPL").upper()
quantite = st.number_input("Combien d'actions veux-tu acheter ?", min_value=1, value=1, step=1)

if st.button("🚀 Valider l'achat", use_container_width=True):
    try:
        action = yf.Ticker(symbole)
        prix = action.history(period="1d")["Close"].iloc[-1]
        cout_total = prix * quantite
        
        st.write(f"Prix unitaire actuel de **{symbole}** : `{prix:.2f} $`")
        st.write(f"Coût total : `{cout_total:.2f} $`")
        
        if cout_total <= solde:
            reste = solde - cout_total
            st.success(f"✅ Transaction validée ! Il te reste **{reste:.2f} $**.")
        else:
            st.error(f"❌ Fonds insuffisants ! Il te manque `{(cout_total - solde):.2f} $`.")
    except Exception:
        st.error("Impossible de récupérer le prix. Vérifie le symbole.")
