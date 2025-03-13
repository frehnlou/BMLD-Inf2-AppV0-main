import streamlit as st

def blutzucker_grafik():
    st.markdown("## 📊 Blutzucker-Grafik")
    if 'daten' in st.session_state and st.session_state['daten']:
        st.markdown("### Verlauf der Blutzuckerwerte")
        blutzuckerwerte = [d['blutzuckerwert'] for d in st.session_state['daten']]
        st.line_chart({"Blutzuckerwert": blutzuckerwerte})
    else:
        st.warning("Noch keine Daten vorhanden.")

if __name__ == "__main__":
    blutzucker_grafik()