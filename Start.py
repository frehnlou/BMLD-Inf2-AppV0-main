import streamlit as st

# Titel in gross und fett
st.markdown("# Blutzucker-Tracker für Diabetiker")

# Kurze Einleitung
st.write("""
Diese App hilft Ihnen, Ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren.
""")

# Infobox mit Hintergrundfarbe
st.markdown("""
<blockquote style="background-color:#E8F0FE; padding:10px; border-radius:5px;">
Diese App hilft Diabetiker:innen, ihre Blutzuckerwerte einfach zu erfassen, zu speichern und zu analysieren.
Sie bietet eine intuitive Benutzeroberfläche zur Eingabe der Werte sowie eine Übersicht der bisherigen Messungen.
</blockquote>
""", unsafe_allow_html=True)

# Autoren und E-Mails
st.write("""
Diese App wurde von **Cristiana Bastos** (<pereicri@students.zhaw.ch>) und  
**Lou-Salomé Frehner** (<frehnlou@students.zhaw.ch>) im Rahmen des Moduls  
'BMLD Informatik 2' an der ZHAW entwickelt.
""")