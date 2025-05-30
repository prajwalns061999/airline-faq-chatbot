# app.py
import streamlit as st


# and might require re-running the app with query params, which we'll avoid for now.
INITIAL_BOT_KEY = "airline_faq" # Default bot

# --- CHATBOT CONFIGURATIONS (Keep this defined early) ---
CHATBOT_CONFIGS = {
    "airline_faq": {
        "display_name": "✈️ SkyConnect Airlines Concierge",
        "page_title": "SkyConnect Chatbot", # Used for initial st.set_page_config
        "page_icon": "✈️",                 # Used for initial st.set_page_config
        "header_title": "✈️ SkyConnect Airlines Concierge",
        "header_subtitle": "Your personal assistant for flight schedules, baggage policies, and more!",
        "header_title_color": "#000001",  # CHANGED TO BLACK
        "header_subtitle_color": "#000001",
        "background_image_url": "https://img.freepik.com/free-photo/airplane-runway-airport-sunset-travel-concept_587448-8154.jpg?ga=GA1.1.1907611749.1748313800&semt=ais_hybrid&w=740",
        "opensearch_index_name": "skyconnect-knowledge-base",
        "initial_assistant_message": "Hi there! I'm your SkyConnect Airlines Concierge. How can I assist you today regarding flights, baggage, or our policies?",
        "assistant_avatar": "✈️",
        "chat_input_placeholder": "Ask about SkyConnect flights or policies...",
        "llm_persona_prompt": """You are SkyConnect Airlines' friendly and helpful assistant...""" # Truncated for brevity
    },
    "university_course": {
        "display_name": "🎓 University Course Advisor",
        "page_title": "University Course Chatbot",
        "page_icon": "🎓",
        "header_title": "🎓 University Course Advisor",
        "header_subtitle": "Ask about course details, prerequisites, and academic programs.",
        "header_title_color": "#000001",
        "header_subtitle_color": "#000001",
        "background_image_url": "https://images.pexels.com/photos/267885/pexels-photo-267885.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "opensearch_index_name": "university-course-knowledge-base",
        "initial_assistant_message": "Hello! I'm the University Course Advisor. Backend for this bot is under construction.",
        "assistant_avatar": "🎓",
        "chat_input_placeholder": "Ask about courses (UI Demo)...",
        "llm_persona_prompt": "Placeholder persona for University Bot."
    },
    "coffee_shop": {
        "display_name": "☕ Coffee Corner Bot",
        "page_title": "Coffee Corner Chatbot",
        "page_icon": "☕",
        "header_title": "☕ Coffee Corner Bot",
        "header_subtitle": "Your guide to our menu, special offers, and opening hours!",
        "header_title_color": "#000001",
        "header_subtitle_color": "#000001",
        "background_image_url": "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "opensearch_index_name": "coffee-shop-knowledge-base",
        "initial_assistant_message": "Welcome to Coffee Corner! Backend for this bot is coming soon.",
        "assistant_avatar": "☕",
        "chat_input_placeholder": "Ask about our coffee (UI Demo)...",
        "llm_persona_prompt": "Placeholder persona for Coffee Bot."
    }
}

# Determine initial config for set_page_config
# If session state has a current bot, use that, otherwise use the default.
# This helps if the user has already interacted and then the script reruns (e.g., saving the file).
if "current_bot_key" in st.session_state and st.session_state.current_bot_key in CHATBOT_CONFIGS:
    _initial_config_for_page = CHATBOT_CONFIGS[st.session_state.current_bot_key]
else:
    _initial_config_for_page = CHATBOT_CONFIGS[INITIAL_BOT_KEY]

st.set_page_config(
    page_title=_initial_config_for_page["page_title"],
    page_icon=_initial_config_for_page["page_icon"],
    layout="wide"
)

# Now import other necessary modules
from bedrock_client import get_embedding, query_llm # Still needed for Airline bot
from opensearch_client import search_chunks # Still needed for Airline bot


# --- Function to set background image and dynamic text colors ---
def set_app_style(bg_url, chat_text_color="#000001"):
    # (Style function remains the same as your last provided version)
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("{bg_url}");
             background-size: cover;
             background-repeat: no-repeat;
             background-attachment: fixed;
             background-position: center;
         }}
         .stChatInputContainer {{
            background-color: rgba(255, 255, 255, 0.8);
         }}
         .stChatMessage {{
            background-color: rgba(240, 242, 246, 0.85) !important;
            border-radius: 0.5rem;
            padding: 10px 15px;
            margin-bottom: 10px;
         }}
         .stChatMessage[data-testid="chatAvatarIcon-user"] + div > div {{
            background-color: rgba(220, 238, 255, 0.85) !important;
         }}
         .stChatMessage[data-testid="chatAvatarIcon-assistant"] + div > div {{
            background-color: rgba(230, 230, 230, 0.85) !important;
         }}

         /* Page header title - uses CSS variable set in markdown */
         .page-header-title {{
             color: #000001; /* Relies on inline style setting this variable */
             text-align: center;
         }}
         /* Page header subtitle - uses CSS variable set in markdown */
         .page-header-subtitle {{
             color: #000001; /* Relies on inline style setting this variable */
             text-align: center;
             font-size: 1.1em;
         }}

         /* Ensure all text content within chat messages is the desired color */
         .stChatMessage div[data-testid="stMarkdownContainer"] * {{ /* Targets all descendant elements */
            color: {chat_text_color} !important;
         }}
         /* Ensures text directly under markdown container (if any) is also colored */
         .stChatMessage div[data-testid="stMarkdownContainer"] {{
             color: {chat_text_color} !important;
         }}
         /* Chat input text color */
         .stChatInputContainer input {{
            color: {chat_text_color} !important;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# --- Function to reset chat state when switching bots ---
def reset_chat_state(new_bot_config_key):
    config = CHATBOT_CONFIGS[new_bot_config_key]
    st.session_state.messages = [
        {"role": "assistant", "content": config["initial_assistant_message"]}
    ]
    st.session_state.current_bot_key = new_bot_config_key


# --- Sidebar for Chatbot Selection ---
st.sidebar.title("Select Chatbot")
bot_display_names = [config["display_name"] for config in CHATBOT_CONFIGS.values()]
bot_keys_map = {config["display_name"]: key for key, config in CHATBOT_CONFIGS.items()}

if "current_bot_key" not in st.session_state:
    st.session_state.current_bot_key = INITIAL_BOT_KEY # Default to airline

default_selectbox_index = 0 # Default to first option
try:
    default_selectbox_index = bot_display_names.index(CHATBOT_CONFIGS[st.session_state.current_bot_key]["display_name"])
except (ValueError, KeyError): # Handle cases where current_bot_key might be invalid
    st.session_state.current_bot_key = INITIAL_BOT_KEY
    default_selectbox_index = bot_display_names.index(CHATBOT_CONFIGS[INITIAL_BOT_KEY]["display_name"])


selected_bot_display_name = st.sidebar.selectbox(
    "Choose a chatbot:",
    options=bot_display_names,
    index=default_selectbox_index,
    key="chatbot_selector_widget"
)
selected_bot_key = bot_keys_map[selected_bot_display_name]

if st.session_state.current_bot_key != selected_bot_key:
    reset_chat_state(selected_bot_key)

current_config = CHATBOT_CONFIGS[st.session_state.current_bot_key]

# --- Apply Dynamic Styling (Background, Text Colors on BG) ---
# This set_app_style call now happens AFTER st.set_page_config
# and AFTER the current_config is determined.
set_app_style(
    current_config["background_image_url"],
    chat_text_color="#000001"
)

# --- Dynamic Page Content (Titles, Subtitles) ---
st.markdown(f"<h1 class='page-header-title' style='--header-title-color: {current_config['header_title_color']};'>{current_config['header_title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='page-header-subtitle' style='--header-subtitle-color: {current_config['header_subtitle_color']};'>{current_config['header_subtitle']}</p>", unsafe_allow_html=True)
st.markdown("---")


# --- Initialize chat history if not already done (e.g., after reset or first run) ---
if "messages" not in st.session_state:
    # This will be based on the current_config after selection or default
    st.session_state.messages = [
        {"role": "assistant", "content": current_config["initial_assistant_message"]}
    ]

# --- Display chat messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=current_config["assistant_avatar"] if message["role"] == "assistant" else "🧑‍💻"):
        st.markdown(message["content"])

# --- User Query Input ---
if user_query := st.chat_input(current_config["chat_input_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_query)

    # --- Assistant Response Logic ---
    with st.chat_message("assistant", avatar=current_config["assistant_avatar"]):
        bot_key = st.session_state.current_bot_key
        
        if bot_key == "airline_faq":
            with st.spinner(f"✈️ SkyConnect is searching for your answer..."):
                message_placeholder = st.empty()
                
                query_embedding = get_embedding(user_query) # Make sure bedrock_client is imported
                results = search_chunks( # Make sure opensearch_client is imported
                    current_config["opensearch_index_name"],
                    query_embedding,
                    k=3
                )
                
                retrieved_chunks_text = [hit['_source']['chunk_text'] for hit in results]
                context = "\n\n---\n\n".join(retrieved_chunks_text)

                full_response = ""
                if not retrieved_chunks_text:
                    answer = "I couldn't find specific information related to your query in my current knowledge base. Could you please try rephrasing, or ask about a different topic like flight schedules or baggage policies?"
                else:
                    answer = query_llm( # Make sure bedrock_client is imported
                        user_query,
                        context,
                        current_config["llm_persona_prompt"]
                    )
                message_placeholder.markdown(answer)
                full_response = answer
        
        elif bot_key == "university_course":
            message_placeholder = st.empty()
            answer = f"Thank you for asking about: '{user_query}'.\n\n**Placeholder:** The backend for the University Course Advisor is currently under development. In a real scenario, I would search our university course database and LLM for an answer here."
            message_placeholder.markdown(answer)
            full_response = answer

        elif bot_key == "coffee_shop":
            message_placeholder = st.empty()
            answer = f"You asked: '{user_query}'.\n\n**Placeholder:** The Coffee Corner Bot's backend is not yet live. If it were, I'd look up our menu or specials to answer your question!"
            message_placeholder.markdown(answer)
            full_response = answer
        
        else: 
            message_placeholder = st.empty()
            answer = "Sorry, an unexpected error occurred with bot selection."
            message_placeholder.markdown(answer)
            full_response = answer
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Footer ---
# st.markdown("---")
# st.markdown("<p style='text-align: center; font-size: 0.9em; color: #FFFFFF;'>Powered by Amazon Bedrock and OpenSearch (for active bots)</p>", unsafe_allow_html=True)