import streamlit as st

st.title("Blutzucker-Tracker für Diabetiker")

st.write("""
Liebe Diabetikerinnen und Diabetiker!🩸

Kennst du das Problem, den Überblick über deine Blutzuckerwerte zu behalten? Mit unserem Blutzucker-Tracker kannst du deine Werte einfach eingeben, speichern und analysieren – alles an einem Ort!

- Was bringt dir die App?
- Schnelle Eingabe deines Blutzuckers (mg/dL)
- Messzeitpunkt wählen (Nüchtern oder nach dem Essen)
- Alle Werte speichern & jederzeit abrufen
- Tabelle & Diagramm, um deine Trends zu erkennen
- Automatische Warnhinweise, wenn dein Blutzucker zu hoch oder zu niedrig ist

Warum diese App?
         
✔ Kein lästiges Papier-Tagebuch mehr

✔ Verfolge deine Werte langfristig & erkenne Muster

✔ Bessere Kontrolle für ein gesünderes Leben mit Diabetes

Einfach testen & deine Blutzuckerwerte im Blick behalten! 🏅
""")

menu = ["Startseite", "Blutzucker-Tracker", "Passwort-Generator"]
wahl = st.sidebar.selectbox("Menü", menu)

if wahl == "Startseite":
    st.subheader("Willkommen zur App")

elif wahl == "Blutzucker-Tracker":
    st.subheader("Blutzucker-Tracker")
    
    # Blutzucker-Tracker
    blutzuckerwert = st.number_input("Gib deinen Blutzuckerwert ein", min_value=0)
    zeitpunkt = st.selectbox("Zeitpunkt", ["Nüchtern", "Nach dem Essen"])
    
    if 'daten' not in st.session_state:
        st.session_state['daten'] = []

    if st.button("Eintrag hinzufügen"):
        st.session_state['daten'].append({"blutzuckerwert": blutzuckerwert, "zeitpunkt": zeitpunkt})
        st.success("Eintrag erfolgreich hinzugefügt")
        
        # Tipps basierend auf dem Blutzuckerwert
        if blutzuckerwert < 70:
            st.warning("Dein Blutzuckerwert ist niedrig. Es wird empfohlen, schnell wirkende Kohlenhydrate wie Saft oder Traubenzucker zu dir zu nehmen.")
        elif blutzuckerwert > 180:
            st.warning("Dein Blutzuckerwert ist erhöht. Es wird empfohlen, deinen Blutzucker regelmäßig zu überwachen und gegebenenfalls Insulin zu verabreichen.")
        
    if st.session_state['daten']:
        df = pd.DataFrame(st.session_state['daten'])
        st.write(df)
        
        fig, ax = plt.subplots()
        for label, df_group in df.groupby("zeitpunkt"):
            df_group.plot(x="zeitpunkt", y="blutzuckerwert", ax=ax, label=label, marker='o')
        st.pyplot(fig)

elif wahl == "Passwort-Generator":
    st.subheader("Passwort-Generator")
    
    # Passwort-Generator
    länge = st.number_input("Passwortlänge", min_value=1, max_value=100, value=8)
    optionen = st.multiselect("Optionen", ["Großbuchstaben", "Zahlen", "Sonderzeichen"])
    
    if st.button("Passwort generieren"):
        passwort = passwort_generieren(länge, optionen)
        st.write(f"Generiertes Passwort: {passwort}")

def passwort_generieren(länge, optionen):
    zeichen_pool = string.ascii_lowercase
    if "Großbuchstaben" in optionen:
        zeichen_pool += string.ascii_uppercase
    if "Zahlen" in optionen:
        zeichen_pool += string.digits
    if "Sonderzeichen" in optionen:
        zeichen_pool += string.punctuation
    
    return ''.join(random.choice(zeichen_pool) for _ in range(länge))