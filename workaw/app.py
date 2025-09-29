import streamlit as st
import pandas as pd
import google.generativeai as genai
from prompt import PROMPT_WORKAW
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime  # << เพิ่มเพื่อเก็บเวลาค้นหา

# --- ตั้งค่า API และ Model เหมือนเดิม ---
genai.configure(api_key="AIzaSyB-MO6y9Nm-NwnRNFRkILWB6fbBw59U29s")

generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",
}

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    safety_settings=SAFETY_SETTINGS,
    generation_config=generation_config,
    system_instruction=PROMPT_WORKAW
)

# --- Streamlit UI ---
st.title("💬 OOP Chatbot")

st.markdown(
    """
    <style>
    /* พื้นหลังหลักแบบ Gradient */
     /* Title styling with gradient */
    h1 {
        background: linear-gradient(135deg, #2d5016, #4a7c59);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
     /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        # background: linear-gradient(180deg, #d4f0d7 0%, #e8f5ea 100%);
        border-right: 2px solid rgba(129, 199, 132, 0.3);
    }
    /* Animation keyframes */
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(200, 240, 198, 0.3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #81c784, #a5d6a7); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #66bb6a, #81c784); }

    /* Error and success message styling */
    .stAlert { border-radius: 12px; border: none; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }

    /* Loading spinner */
    .stSpinner { color: #4caf50; }

    /* Custom container for better spacing */
    .chat-container { max-width: 800px; margin: 0 auto; padding: 20px; }

    /* Responsive design */
    @media (max-width: 768px) {
        h1 { font-size: 2rem; }
        div.stChatMessage { margin: 5px 0; padding: 12px 15px; }
    }
      
    /* ซ่อน Streamlit branding */
     MainMenu {visibility: hidden;}
     footer {visibility: hidden;}
    # header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Load Excel
file_path = "C:/Users/User/Downloads/workaw_chatbot/workaw_chatbot/workaw/workaw_data.xlsx"
try:
    df = pd.read_excel(file_path)
    excel_context = (
        "นี่คือฐานข้อมูลจาก Excel:\n"
        + df.head(50).to_string(index=False)
        + "\n\n**โปรดตอบโดยอ้างอิงจากข้อมูลใน Excel เท่านั้น** "
        "ถ้าไม่มีข้อมูลที่ตรง ให้ตอบว่า 'ไม่มีข้อมูลใน Excel ค่ะ'"
    )
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# Initialize session_state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "สวัสดีค่ะ น้อง ๆ มีเรื่องอะไรสงสัยเกี่ยวกับ OOP หรอคะ",
        }
    ]

# << เพิ่มตัวแปรเก็บประวัติการค้นหา >>
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []  # [{"text": "...", "time": "..."}]

# Sidebar: Image + Clear History + Search History
with st.sidebar:
    st.image("LOGO-03-01.png", caption="OOP BOTCHAT")

    st.markdown("---")
    st.markdown("### ⚙️ การจัดการแชท")
    if st.button("🗑️ Clear History"):
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "สวัสดีค่ะ น้อง ๆ มีเรื่องอะไรสงสัยเกี่ยวกับ OOP หรอคะ",
            }
        ]
        st.session_state["search_history"] = []  # ล้างประวัติการค้นหา
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔎 ประวัติการค้นหา")
    if st.session_state["search_history"]:
        for i, item in enumerate(reversed(st.session_state["search_history"]), start=1):
            st.markdown(
                f"**{i}.** {item['text']}  \n"
                f"<small>🕒 {item['time']}</small>",
                unsafe_allow_html=True
            )
        if st.button("🧹 ล้างเฉพาะประวัติการค้นหา"):
            st.session_state["search_history"] = []
            st.rerun()
    else:
        st.caption("ยังไม่มีประวัติการค้นหา")

# Display chat messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # >> บันทึกลงประวัติการค้นหา
    st.session_state["search_history"].append({
        "text": prompt.strip(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # ถ้าต้องการจำกัดจำนวนล่าสุด 100 รายการ ให้ใช้บรรทัดนี้:
    # st.session_state["search_history"] = st.session_state["search_history"][-100:]

    history = [
        {"role": m["role"], "parts": [{"text": m["content"]}]} for m in st.session_state["messages"]
    ]

    if not hasattr(st.session_state, "excel_added"):
        history.insert(1, {"role": "user", "parts": [{"text": excel_context}]})
        st.session_state["excel_added"] = True

    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(prompt)

    st.session_state["messages"].append({"role": "assistant", "content": response.text})
    st.chat_message("assistant").write(response.text)
