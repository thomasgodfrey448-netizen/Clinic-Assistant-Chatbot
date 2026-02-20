import streamlit as st
import html

st.set_page_config(page_title="Clinic Assistant Chatbot", page_icon="💬")

st.title("Clinic Assistant Chatbot 💬")
st.write("Start booking appointments and receiving basic symptom guidance, or ask any questions you have about our clinic services.")

responses = {
    "hi": "Hello, how are you?",
    "hey": "Hello, how are you?",
    "hellow": "Hi, how are you?",
    "hello": "Hi, how are you?",
    "am good": "Welcome to Clinic Assistant. Do you have any questions?",
    "good": "Welcome to Clinic Assistant. Do you have any questions?",
    "i'm good": "Welcome to Clinic Assistant. Do you have any questions?",
    "fine": "Welcome to Clinic Assistant. Do you have any questions?",
    "am fine": "Welcome to Clinic Assistant. Do you have any questions?",
    "i'm fine": "Welcome to Clinic Assistant. Do you have any questions?",
    "yap": "What do you want to know? i can help with booking appointments and giving basic symptom guidance.",
    "yes i have": "What do you want to know? i can help with booking appointments and giving basic symptom guidance.",
    "yes i have a question": "What do you want to know? i can help with booking appointments and giving basic symptom guidance.",
    "yes": "What do you want to know? i can help with booking appointments and giving basic symptom guidance.",
    "ok thank you": "You're welcome! thank you for using Clinic Assistant. If you have any more questions, feel free to ask.",
    "thank you": "You're welcome! thank you for using Clinic Assistant. If you have any more questions, feel free to ask.",
    "ok": "You're welcome! thank you for using Clinic Assistant. If you have any more questions, feel free to ask.",
    "thank you for the service": "You're welcome! thank you for using Clinic Assistant. If you have any more questions, feel free to ask."
}


def triage(symptoms_text: str) -> str:
    s = symptoms_text.lower()
    urgent = [
        "chest pain",
        "difficulty breathing",
        "shortness of breath",
        "severe bleeding",
        "unconscious",
        "fainting"
    ]
    if any(k in s for k in urgent):
        return "These symptoms can be serious. Seek emergency care or call your local emergency number immediately."
    if "fever" in s or "cough" in s or "sore throat" in s:
        return "It may be an infection. Rest, stay hydrated, consider paracetamol for fever. If symptoms worsen or persist beyond 48 hours, book a clinic visit."
    return "Monitor your symptoms, stay hydrated and rest. If symptoms persist or you are concerned, please book an appointment."

# Create memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Simple CSS for left (bot) and right (user) bubbles, plus labels
st.markdown(
    """
    <style>
    .chat-bubble{padding:10px;border-radius:12px;max-width:70%;word-wrap:break-word}
    .user{background:#DCF8C6;color:#000}
    .bot{background:#F1F0F0;color:#000}
    .label{font-size:12px;color:#555;margin-bottom:4px}
    </style>
    """,
    unsafe_allow_html=True,
)

# Display previous messages with left/right alignment
for message in st.session_state.messages:
    content = html.escape(message["content"]).replace("\n", "<br>")
    if message["role"] == "user":
        st.markdown(
            f'''<div style="display:flex;flex-direction:column;align-items:flex-end;margin:8px;">
                <div class="label">Me</div>
                <div class="chat-bubble user">{content}</div>
            </div>''',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'''<div style="display:flex;flex-direction:column;align-items:flex-start;margin:8px;">
                <div class="label">Bot</div>
                <div class="chat-bubble bot">{content}</div>
            </div>''',
            unsafe_allow_html=True,
        )

# Chat input (fixed bottom)
user_input = st.chat_input("Type a message and press Enter")

if user_input:
    # Save user message (RIGHT)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(
        f'''<div style="display:flex;flex-direction:column;align-items:flex-end;margin:8px;">
                <div class="label">Me</div>
                <div class="chat-bubble user">{html.escape(user_input)}</div>
            </div>''',
        unsafe_allow_html=True,
    )

    # Bot response logic with appointment and symptom flows
    user_text = user_input.lower().strip()

    # Initialize booking state if not present
    if "booking_step" not in st.session_state:
        st.session_state.booking_step = None
    if "booking" not in st.session_state:
        st.session_state.booking = {}

    # Initialize symptom state
    if "symptom_step" not in st.session_state:
        st.session_state.symptom_step = None

    bot_reply = None

    # If we're in the middle of booking
    if st.session_state.booking_step:
        step = st.session_state.booking_step
        if step == "ask_date":
            st.session_state.booking["date"] = user_input
            st.session_state.booking_step = "ask_time"
            bot_reply = "What time would you prefer?"
        elif step == "ask_time":
            st.session_state.booking["time"] = user_input
            st.session_state.booking_step = "ask_doctor"
            bot_reply = "Which doctor or specialty would you like (e.g., General, Pediatrics)?"
        elif step == "ask_doctor":
            st.session_state.booking["doctor"] = user_input
            st.session_state.booking_step = "ask_contact"
            bot_reply = "Please provide a contact name and phone number."
        elif step == "ask_contact":
            st.session_state.booking["contact"] = user_input
            # Confirm booking
            b = st.session_state.booking
            bot_reply = (
                f"Appointment booked: {b.get('date','')} at {b.get('time','')} with {b.get('doctor','')}. "
                f"Contact: {b.get('contact','')}. We will reach out to confirm."
            )
            st.session_state.booking_step = None
            st.session_state.booking = {}

    # If we're in the middle of symptom checking
    elif st.session_state.symptom_step:
        step = st.session_state.symptom_step
        if step == "ask_symptoms":
            symptoms_text = user_input
            bot_reply = triage(symptoms_text)
            st.session_state.symptom_step = None

    else:
        # Start booking flow
        if "book" in user_text or "appointment" in user_text:
            st.session_state.booking = {}
            st.session_state.booking_step = "ask_date"
            bot_reply = "Sure — what date would you like to book (e.g., 2026-03-15)?"

        # Start symptom checker
        elif "symptom" in user_text or user_text.startswith("i have") or any(w in user_text for w in ["pain","fever","cough","headache","nausea"]):
            st.session_state.symptom_step = "ask_symptoms"
            bot_reply = "I'm a basic symptom checker. Please list your symptoms separated by commas."

        # Smalltalk / fallback
        elif user_text == "bye":
            bot_reply = "Goodbye 👋"
        elif user_text in responses:
            bot_reply = responses[user_text]
        else:
            bot_reply = "Sorry, I can help with booking appointments and giving basic symptom guidance — would you like to 'book appointment' or describe your symptoms?"

    # Save bot message (LEFT)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.markdown(
        f'''<div style="display:flex;flex-direction:column;align-items:flex-start;margin:8px;">
                <div class="label">Bot</div>
                <div class="chat-bubble bot">{html.escape(bot_reply)}</div>
            </div>''',
        unsafe_allow_html=True,
    )

# Restart button
if st.button("Restart Chat"):
    st.session_state.messages = []

