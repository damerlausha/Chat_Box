import streamlit as st 
from datetime import datetime
import hashlib
import json
import os
import tempfile
import secrets
from urllib.parse import quote
import urllib.error
import urllib.request
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import WebRtcMode, webrtc_streamer
st.set_page_config()
st.markdown("""
<style>
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],main{background:#FFF0F5 !important}
[data-testid="stHeader"]{background:rgba(255,240,245,.92) !important}
.stApp label,.stApp button,.stApp input,.stApp textarea,.stApp [data-testid="stWidgetLabel"] p{color:#000 !important}
div[data-testid="stTextInput"] input{color:#fff !important;-webkit-text-fill-color:#fff !important;caret-color:#fff !important}
div[data-testid="stChatInput"] textarea{color:#fff !important}
div[data-testid="stSelectbox"] input,
div[data-testid="stSelectbox"] [role="combobox"]{color:#fff !important}
button,button *{color:#fff !important}
.stButton>button,.stButton>button *,[data-testid="stAudioInput"] button,[data-testid="stAudioInput"] button *,[data-testid="stFileUploader"] button,[data-testid="stFileUploader"] button *{color:#fff !important}
[style*="background: black"],[style*="background-color: black"],[style*="background: rgb(0, 0, 0)"],[style*="background-color: rgb(0, 0, 0)"]{color:#fff !important}
.chat{padding:10px;border-radius:15px;margin:5px;animation:message-bounce 0.55s cubic-bezier(.2,.8,.2,1) both;transition:transform 0.2s ease,box-shadow 0.2s ease}
.chat:hover{transform:translateY(-3px) scale(1.01);box-shadow:0 6px 14px rgba(0,0,0,.14)}
.message-meta{font-size:11px;color:#555;white-space:nowrap}
.voice-label{display:inline-block;color:#1769aa;font-weight:600;animation:voice-pulse 1.8s ease-in-out infinite}
.chat-row{display:flex;align-items:flex-end;justify-content:space-between;gap:12px}
.chat-main{display:flex;flex-direction:column;gap:4px;min-width:0}
.chat-main b{display:inline-block;animation:name-pop 0.45s ease-out both}
.message-text{overflow-wrap:anywhere}
.john .chat-row{flex-direction:row-reverse}
.john{background:linear-gradient(135deg,#D9EEFF,#A9D4F5);color:#102A43;text-align:right} 
.alice{background:linear-gradient(135deg,#FDEAF3,#F1C9DC);color:#3D1F2B;text-align:left}
.bob{background:linear-gradient(135deg,#FFF8CC,#F2D477);color:#4A3A00;text-align:left}
.carol{background:linear-gradient(135deg,#F0E9FF,#D3C1F5);color:#2D1B4E;text-align:left}
.david{background:linear-gradient(135deg,#FFF0D1,#F7CE91);color:#4A2A00;text-align:left}
.ai{background:linear-gradient(135deg,#E2FFF8,#B7E8DB);color:#123C35;text-align:left}
.header{position:relative;overflow:hidden;background:#B7E4C7;color:#12372A;padding:15px;border-radius:10px;font-size:28px;text-align:center;font-weight:bold;animation:header-pop 0.8s cubic-bezier(.2,1.4,.4,1) both}
.header::after{content:"";position:absolute;top:0;left:-35%;width:25%;height:100%;background:rgba(255,255,255,.5);transform:skewX(-20deg);animation:shine 2.8s ease-in-out 0.8s infinite}
div[data-testid="stRadio"]{width:100%;box-sizing:border-box;color:blue;padding:0;animation:slide-in 0.35s ease-out}
div[data-testid="stRadio"] label{display:flex;align-items:center;width:100%;box-sizing:border-box;background:transparent;color:blue !important;padding:20px 24px;margin:0 0 12px;border-radius:10px;font-size:20px;transition:transform 0.25s ease,box-shadow 0.25s ease,background-color 0.25s ease}
div[data-testid="stRadio"] label:hover{transform:translateX(8px);background-color:#FFF1B8;box-shadow:0 5px 14px rgba(0,0,0,.12)}
div[data-testid="stRadio"] p{color:blue !important;font-size:20px}
div[data-testid="stRadio"] label:has(input:checked){background:rgba(144,238,144,.35);box-shadow:0 0 0 2px rgba(0,128,0,.2),0 6px 16px rgba(0,0,0,.12);animation:selected-pop 0.45s ease-out}
div[data-testid="stSelectbox"],div[data-testid="stChatInput"]{animation:control-rise 0.55s ease-out both}
div[data-testid="stChatInput"] textarea{transition:box-shadow 0.25s ease,border-color 0.25s ease}
div[data-testid="stChatInput"] textarea:focus{border-color:#25D366;box-shadow:0 0 0 3px rgba(37,211,102,.2),0 4px 14px rgba(37,211,102,.18)}
button{transition:transform 0.2s ease,box-shadow 0.2s ease,background-color 0.2s ease}
button:hover{transform:translateY(-2px);box-shadow:0 6px 14px rgba(0,0,0,.16)}
button:active{transform:translateY(1px) scale(.98)}
button:focus-visible{outline:3px solid rgba(37,211,102,.45);outline-offset:3px}
@keyframes slide-in {
    from {opacity:0; transform:translateY(12px)}
    to {opacity:1; transform:translateY(0)}
}
@keyframes header-pop {
    0% {opacity:0; transform:scale(.85) rotate(-2deg)}
    70% {transform:scale(1.04) rotate(.5deg)}
    100% {opacity:1; transform:scale(1) rotate(0)}
}
@keyframes shine {
    0%, 55% {left:-35%}
    100% {left:125%}
}
@keyframes message-bounce {
    0% {opacity:0; transform:translateY(18px) scale(.96)}
    70% {opacity:1; transform:translateY(-3px) scale(1.01)}
    100% {opacity:1; transform:translateY(0) scale(1)}
}
@keyframes name-pop {
    from {opacity:0;transform:translateX(-8px)}
    to {opacity:1;transform:translateX(0)}
}
@keyframes selected-pop {
    0% {transform:scale(1)}
    60% {transform:scale(1.03)}
    100% {transform:scale(1)}
}
@keyframes control-rise {
    from {opacity:0;transform:translateY(10px)}
    to {opacity:1;transform:translateY(0)}
}
@keyframes voice-pulse {
    0%, 100% {opacity:.7}
    50% {opacity:1}
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {animation-duration:.01ms !important;animation-iteration-count:1 !important;transition-duration:.01ms !important}
}
</style>
""", unsafe_allow_html=True)
users = ["Minny", "Lilly", "Kanchu", "Kushi", "Nani"]
chat_types = ["One-to-One", "Group Chat", "Voice Chat", "Video Chat", "Public Chat" , "AI Chat"]

def generate_ai_reply(messages):
    conversation = [
        {
            "role": "assistant" if sender == "AI Assistant" else "user",
            "content": text,
        }
        for sender, text, *_ in messages[-20:]
        if text
    ]
    request_data = json.dumps({
        "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "messages": [
            {
                "role": "system",
                "content": "Answer clearly and helpfully. Use the conversation history when relevant. If you are uncertain, say so rather than inventing facts.",
            },
            *conversation,
        ],
        "stream": False,
    }).encode("utf-8")
    request = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=request_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
        answer = result.get("message", {}).get("content", "").strip()
        return answer or "The local AI returned an empty response. Please try again."
    except urllib.error.HTTPError as error:
        try:
            error_details = json.loads(error.read().decode("utf-8")).get("error", "")
        except (UnicodeDecodeError, json.JSONDecodeError):
            error_details = ""
        if error.code == 404:
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            return f"Local model '{model}' was not found. Run `ollama pull {model}` and try again."
        return f"The local AI service returned an error: {error_details or error.code}."
    except urllib.error.URLError:
        return "Could not connect to Ollama. Start the Ollama app and try again."
    except TimeoutError:
        return "The local AI took too long to respond. Please try again."
    except json.JSONDecodeError:
        return "Ollama returned an invalid response. Please try again."
if "active_chat_mode" not in st.session_state:
    st.session_state.active_chat_mode = None

if st.session_state.active_chat_mode is None:
    st.markdown('<div class="header">Chat Bot</div>', unsafe_allow_html=True)
    selected_chat_type = st.radio(
        " ",
        chat_types,
        index=None,
        horizontal=False,
        label_visibility="collapsed",
    )
    if selected_chat_type:
        st.session_state.active_chat_mode = selected_chat_type
        st.rerun()
    st.stop()

chat_mode = st.session_state.active_chat_mode
st.markdown(f'<div class="header">{chat_mode}</div>', unsafe_allow_html=True)
if chat_mode == "One-to-One":
    st.markdown(
        """
        <style>
        div[data-testid="stChatInput"] textarea,
        div[data-testid="stSelectbox"] input,
        div[data-testid="stSelectbox"] [role="combobox"] {
            color:#fff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
if st.button("Change Chat Type"):
    st.session_state.active_chat_mode = None
    st.rerun()

if chat_mode == "Group Chat":
    conversation_key = "group"
    user = st.selectbox("Select User", users)
elif chat_mode == "Public Chat":
    conversation_key = "public"
    user = st.selectbox("Select User", users)
elif chat_mode == "AI Chat":
    current_user = st.selectbox("Your Name", users)
    conversation_key = f"ai:{current_user}"
    user = current_user
elif chat_mode == "One-to-One":
    current_user = st.selectbox("Your Name", users)
    contact_options = [name for name in users if name != current_user]
    contact = st.selectbox("Chat With", contact_options)
    conversation_key = f"one-to-one:{current_user}:{contact}"
    user = current_user
elif chat_mode == "Voice Chat":
    conversation_key = "voice"
    user = st.selectbox("Select User", users)
elif chat_mode == "Video Chat":
    conversation_key = "video"
    user = st.selectbox("Select User", users)

if "conversations" not in st.session_state:
    st.session_state.conversations = {"group": []}
messages = st.session_state.conversations.setdefault(conversation_key, [])
recording_path = os.path.join(
    tempfile.gettempdir(),
    f"chat_video_{hashlib.sha256(conversation_key.encode()).hexdigest()[:12]}.mp4",
)
msg = None if chat_mode in ("Voice Chat", "Video Chat") else st.chat_input("Type your message...")
if msg:
    message_time = datetime.now()
    messages.append((user, msg, message_time.strftime("%H:%M"), message_time.strftime("%d %b %Y")))
    if chat_mode == "AI Chat":
        assistant_time = datetime.now()
        messages.append(("AI Assistant", generate_ai_reply(messages), assistant_time.strftime("%H:%M"), assistant_time.strftime("%d %b %Y")))
if "voice_sent" not in st.session_state:
    st.session_state.voice_sent = {}
voice_message = None
if chat_mode not in ("Video Chat", "AI Chat") and not st.session_state.voice_sent.get(conversation_key, False):
    voice_message = st.audio_input("Record a voice message")
if voice_message:
    audio_bytes = voice_message.getvalue()
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()
    if "voice_hashes" not in st.session_state:
        st.session_state.voice_hashes = {}
    if st.session_state.voice_hashes.get(conversation_key) != audio_hash:
        message_time = datetime.now()
        messages.append((user, "", message_time.strftime("%H:%M"), message_time.strftime("%d %b %Y"), audio_bytes))
        st.session_state.voice_hashes[conversation_key] = audio_hash
        st.session_state.voice_sent[conversation_key] = True
if chat_mode == "Video Chat":
    if "video_room_code" not in st.session_state:
        st.session_state.video_room_code = f"group-chat-{secrets.token_hex(12)}"
    video_room_code = st.text_input("Video call room code", key="video_room_code")
    st.caption("Share this room code with the people you want in the call. In-call chat is for people who join the same room.")
    if video_room_code.strip():
        room_url = f"https://meet.jit.si/{quote(video_room_code.strip(), safe='')}"
        st.link_button("Join video call", room_url, use_container_width=True)
if "video_sent" not in st.session_state:
    st.session_state.video_sent = {}
video_message = None
video_context = None
if chat_mode == "Video Chat" and not st.session_state.video_sent.get(conversation_key, False):
    video_message = st.file_uploader("Upload a video message", type=["mp4", "mov", "webm"])
    st.markdown('<p style="color: #000;">Or record a video with your camera and microphone</p>', unsafe_allow_html=True)
    video_context = webrtc_streamer(
        key="video-recorder",
        mode=WebRtcMode.SENDRECV,
        media_stream_constraints={"video": True, "audio": True},
        in_recorder_factory=lambda: MediaRecorder(recording_path, format="mp4"),
    )
if video_message:
    video_bytes = video_message.getvalue()
    video_hash = hashlib.sha256(video_bytes).hexdigest()
    if "video_hashes" not in st.session_state:
        st.session_state.video_hashes = {}
    if st.session_state.video_hashes.get(conversation_key) != video_hash:
        message_time = datetime.now()
        messages.append((user, "", message_time.strftime("%H:%M"), message_time.strftime("%d %b %Y"), "video", video_bytes))
        st.session_state.video_hashes[conversation_key] = video_hash
        st.session_state.video_sent[conversation_key] = True
if (
    chat_mode == "Video Chat"
    and video_context is not None
    and not video_context.state.playing
    and os.path.exists(recording_path)
):
    with open(recording_path, "rb") as recording_file:
        recorded_video = recording_file.read()
    if recorded_video:
        video_hash = hashlib.sha256(recorded_video).hexdigest()
        if "video_hashes" not in st.session_state:
            st.session_state.video_hashes = {}
        if st.session_state.video_hashes.get(conversation_key) != video_hash:
            message_time = datetime.now()
            messages.append((user, "", message_time.strftime("%H:%M"), message_time.strftime("%d %b %Y"), "video", recorded_video))
            st.session_state.video_hashes[conversation_key] = video_hash
            st.session_state.video_sent[conversation_key] = True
    os.remove(recording_path)
for message in messages:
    if len(message) == 6:
        user, msg, time, date, media_type, media_bytes = message
    elif len(message) == 5:
        user, msg, time, date, media_bytes = message
        media_type = "audio"
    elif len(message) == 4:
        user, msg, time, date = message
        media_bytes = None
        media_type = None
    else:
        user, msg, time = message
        date = ""
        media_bytes = None
        media_type = None
    css = {
        "Minny": "john",
        "Lilly": "alice",
        "Kanchu": "bob",
        "Kushi": "carol",
        "Nani": "david",
        "John": "john",
        "Alice": "alice",
        "Bob": "bob",
        "Carol": "carol",
        "David": "david",
        "AI Assistant": "ai",
    }.get(user, "alice")
    date_html = f" {date}" if date else ""
    if msg:
        message_html = f'<span class="message-text">{msg}</span>'
    else:
        media_label = "Video message" if media_type == "video" else "Voice message"
        message_html = f'<span class="voice-label">{media_label}</span>'
    st.markdown(f'<div class="chat {css}"><div class="chat-row"><div class="chat-main"><b>{user}</b>{message_html}</div><small class="message-meta">{time}{date_html}</small></div></div>', unsafe_allow_html=True)
    if media_bytes:
        if media_type == "video":
            st.video(media_bytes)
        else:
            st.audio(media_bytes, format="audio/wav")
if st.button("Clear Chat"):
    messages.clear()
    st.session_state.voice_sent[conversation_key] = False
    st.session_state.video_sent[conversation_key] = False
    if os.path.exists(recording_path):
        os.remove(recording_path)
    st.rerun()