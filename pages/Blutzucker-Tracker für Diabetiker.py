import streamlit as st

st.title("Blutzucker-Tracker für Diabetiker")

st.write("""
Diabetiker!🩸

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

Einfach testen & deine Blutzuckerwerte im Blick behalten! 🚀
""")

menu = ["Home", "Blutzucker-Tracker", "Passwort-Generator"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Willkommen zur App")

elif choice == "Blutzucker-Tracker":
    st.subheader("Blutzucker-Tracker")
    
    # Blood Sugar Tracker
    glucose_level = st.number_input("Enter your blood sugar level", min_value=0)
    time_of_day = st.selectbox("Time of day", ["Fasting", "After Meal"])
    
    if 'data' not in st.session_state:
        st.session_state['data'] = []

    if st.button("Add Entry"):
        st.session_state['data'].append({"glucose_level": glucose_level, "time_of_day": time_of_day})
        st.success("Entry added successfully")
    
    if st.session_state['data']:
        df = pd.DataFrame(st.session_state['data'])
        st.write(df)
        fig, ax = plt.subplots()
        for label, df_group in df.groupby("time_of_day"):
            df_group.plot(x="time_of_day", y="glucose_level", ax=ax, label=label, marker='o')
        st.pyplot(fig)

elif choice == "Passwort-Generator":
    st.subheader("Passwort-Generator")
    
    # Password Generator
    length = st.number_input("Password length", min_value=1, max_value=100, value=8)
    options = st.multiselect("Options", ["Uppercase Letters", "Numbers", "Special Characters"])
    
    if st.button("Generate Password"):
        password = generate_password(length, options)
        st.write(f"Generated Password: {password}")

def generate_password(length, options):
    char_pool = string.ascii_lowercase
    if "Uppercase Letters" in options:
        char_pool += string.ascii_uppercase
    if "Numbers" in options:
        char_pool += string.digits
    if "Special Characters" in options:
        char_pool += string.punctuation
    
    return ''.join(random.choice(char_pool) for _ in range(length))