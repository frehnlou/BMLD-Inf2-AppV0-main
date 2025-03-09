import streamlit as st
import pandas as pd

st.title("Blutzucker-Tracker für Diabetiker")

st.write("""
Diese App hilft Diabetiker:innen, ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren.
Sie bietet eine intuitive Benutzeroberfläche zur Eingabe der Werte sowie eine Übersicht der bisherigen Messungen.
""")

# !! WICHTIG: Eure Emails müssen in der App erscheinen!!

# Streamlit über den Text unten direkt in die App - cool!
st.markdown("""
Diese App wurde von folgenden Personen entwickelt:
- Cristiana Bastos  (pereicri@students.zhaw.ch)
- Lou-Salomé Frehner (frehnlou@students.zhaw.ch)

Diese App ist das leere Gerüst für die App-Entwicklung im Modul Informatik 2 (BMLD/ZHAW)
""")