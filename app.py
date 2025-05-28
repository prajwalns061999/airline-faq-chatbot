import streamlit as st
from bedrock_client import get_embedding, query_llm
from opensearch_client import search_chunks

st.set_page_config(page_title="SkyConnect Chatbot", page_icon="✈️", layout="wide") # Changed to wide layout

# --- Function to set background image ---
def set_bg_from_url(url):
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("{url}");
             background-size: cover;
             background-repeat: no-repeat;
             background-attachment: fixed;
             background-position: center;
         }}
         /* Make chat input background slightly transparent to blend better */
         .stChatInputContainer {{
            background-color: rgba(255, 255, 255, 0.8); /* White with 80% opacity */
         }}
         /* Adjust chat message background for readability */
         .stChatMessage {{
            background-color: rgba(240, 242, 246, 0.85); /* Streamlit's default light gray with opacity */
            border-radius: 0.5rem;
            padding: 10px 15px;
            margin-bottom: 10px;
         }}
         .stChatMessage[data-testid="chatAvatarIcon-user"] + div > div {{
            background-color: rgba(220, 238, 255, 0.85); /* Lighter blue with opacity for user */
         }}
         .stChatMessage[data-testid="chatAvatarIcon-assistant"] + div > div {{
            background-color: rgba(230, 230, 230, 0.85); /* Lighter grey with opacity for assistant */
         }}

         /* Ensure text is readable on the background */
         h1, p, .stMarkdown, .stSubheader, .stTextInput > div > div > input, .stButton > button {{
             color: #FFFFFF; /* Default to white for primary text if background is dark */
         }}
         /* You might need to adjust specific elements if white isn't suitable for all */
         /* For example, if some parts of the image are very light */
         .stChatMessage p, .stChatInputContainer input {{
            color: #000001 !important; /* Black text for chat messages and input for contrast */
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# --- !!! DIRECT IMAGE URL !!! ---
# direct_image_url = "https://img.freepik.com/free-photo/jumbo-jet-flying-sky_23-2150895693.jpg?ga=GA1.1.1907611749.1748313800&semt=ais_hybrid&w=740"
direct_image_url = "https://img.freepik.com/free-photo/close-up-man-prepared-traveling_23-2151030922.jpg?ga=GA1.1.1907611749.1748313800&semt=ais_hybrid&w=740" 
set_bg_from_url(direct_image_url)

# --- Page Styling and Title ---
st.markdown("<h1 style='text-align: center; color: #004A99;'>✈️ SkyConnect Airlines Concierge</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #000000; font-size: 1.1em;'>Your personal assistant for flight schedules, baggage policies, and more!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm your SkyConnect Airlines Concierge. How can I assist you today regarding flights, baggage, or our policies?"}
    ]

# --- Display chat messages from history on app rerun ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✈️" if message["role"] == "assistant" else "🧑‍💻"):
        st.markdown(message["content"])

# --- User Query Input using st.chat_input ---
if user_query := st.chat_input("Ask me anything about SkyConnect Airlines..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    # Display user message in chat message container
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_query)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="✈️"):
        with st.spinner("✈️ SkyConnect is searching for your answer..."):
            message_placeholder = st.empty() # For streaming-like effect if LLM supported it easily
            
            # 1. Embed user query
            query_embedding = get_embedding(user_query)

            # 2. Retrieve context from OpenSearch
            # Consider adding a k parameter to search_chunks if you want to vary number of results
            results = search_chunks("skyconnect-knowledge-base", query_embedding, k=3) # k=3 for more focused context
            
            retrieved_chunks_text = [hit['_source']['chunk_text'] for hit in results]
            context = "\n\n---\n\n".join(retrieved_chunks_text) # Added separator for clarity

            full_response = ""
            if not retrieved_chunks_text:
                answer = "I couldn't find specific information related to your query in my current knowledge base. Could you please try rephrasing, or ask about a different topic like flight schedules or baggage policies?"
                context_for_display = "No relevant context was retrieved from the knowledge base for this query."
            else:
                # 3. Query LLM for final answer
                answer = query_llm(user_query, context)
                context_for_display = retrieved_chunks_text

            message_placeholder.markdown(answer)
            full_response = answer
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # # Optional: Display retrieved context in an expander
            # if retrieved_chunks_text: # Only show if context was actually used
            #     with st.expander("🔍 View Retrieved Context Snippets"):
            #         for idx, chunk in enumerate(context_for_display if isinstance(context_for_display, list) else [context_for_display], 1):
            #             st.info(f"**Context Snippet {idx}:**\n{chunk}")
            # elif context_for_display: # For the "No relevant context" message
            #      with st.expander("🔍 Retrieval Information"):
            #         st.warning(context_for_display)


# # --- Footer ---
# st.markdown("---")
# st.markdown("<p style='text-align: center; font-size: 0.9em; color: #777;'>Powered by Amazon Bedrock (Titan & Claude) and OpenSearch</p>", unsafe_allow_html=True)

# # --- Optional: Clear chat history button ---
# def clear_chat_history():
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Chat history cleared. How can I help you now?"}
#     ]
#     # Potentially clear other session state variables if needed
# st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

# # Add a little more style
# st.markdown("""
# <style>
#     .stChatMessage {
#         border-radius: 10px;
#         padding: 10px 15px;
#         margin-bottom: 10px;
#     }
#     .stChatMessage[data-testid="chatAvatarIcon-user"] + div {
#         background-color: #E6F3FF; /* Light blue for user */
#     }
#     .stChatMessage[data-testid="chatAvatarIcon-assistant"] + div {
#         background-color: #F0F0F0; /* Light grey for assistant */
#     }
#     .stButton>button {
#         width: 100%;
#     }
# </style>
# """, unsafe_allow_html=True)