import streamlit as st

def blutzucker_werte():
    st.set_page_config(page_title="Blutzucker Werte", layout="wide")
    
    # Abstand nach oben für bessere Platzierung
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("## 📋 Blutzucker-Werte")

    if 'daten' in st.session_state and st.session_state['daten']:
        st.markdown("### Gespeicherte Blutzuckerwerte")
        st.table(st.session_state['daten'])
        
        # Durchschnitt berechnen
        durchschnitt = sum(d['blutzuckerwert'] for d in st.session_state['daten']) / len(st.session_state['daten'])
        
        # Durchschnittswert anzeigen
        st.markdown(f"*Durchschnittlicher Blutzuckerwert:* {durchschnitt:.2f} mg/dL")
    else:
        st.warning("Noch keine Daten vorhanden.")

if __name__ == "__main__":
    blutzucker_werte()