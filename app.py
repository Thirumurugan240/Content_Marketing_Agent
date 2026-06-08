import time
import uuid
from threading import Thread

import streamlit as st

from crew import run_crew

st.set_page_config(page_title="AI Content Writer Crew", page_icon="📝", layout="wide")

AGENTS_ORDER = ["Trend Researcher", "Content Writer", "SEO Specialist"]
AGENT_ICONS = {
    "Trend Researcher": "🔎",
    "Content Writer": "✍️",
    "SEO Specialist": "📈",
}


if "chats" not in st.session_state:
    st.session_state.chats = {}
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None


def new_chat():
    st.session_state.active_chat_id = None


def open_chat(chat_id: str):
    st.session_state.active_chat_id = chat_id


with st.sidebar:
    st.title("💬 Chats")
    st.button("➕ New Chat", on_click=new_chat, use_container_width=True)
    st.markdown("---")

    if not st.session_state.chats:
        st.caption("No chats yet. Start one on the right.")
    else:
        for chat_id, chat in reversed(list(st.session_state.chats.items())):
            label = chat["topic"] if chat["topic"] else "Untitled"
            is_active = chat_id == st.session_state.active_chat_id
            st.button(
                ("👉 " if is_active else "📝 ") + label[:40],
                key=f"open_{chat_id}",
                on_click=open_chat,
                args=(chat_id,),
                use_container_width=True,
            )


st.title("📝 AI Content Writer Crew")


def render_status(placeholders, status):
    for agent_name, ph in placeholders.items():
        icon = AGENT_ICONS[agent_name]
        state = status[agent_name]
        if state == "pending":
            ph.info(f"{icon} **{agent_name}** — ⏳ Pending")
        elif state == "working":
            ph.warning(f"{icon} **{agent_name}** — 🔄 Working...")
        elif state == "done":
            ph.success(f"{icon} **{agent_name}** — ✅ Completed")


if st.session_state.active_chat_id is None:
    st.write(
        "Enter a topic. Three CrewAI agents will work together: "
        "**Researcher** → **Writer** → **SEO Specialist**. "
        "Live progress is shown for each agent."
    )
    topic = st.text_input("Enter your topic:", placeholder="e.g. Artificial Intelligence in Healthcare")

    if st.button("Generate Content", type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            st.subheader("Agent Progress")
            placeholders = {name: st.empty() for name in AGENTS_ORDER}

            status = {name: "pending" for name in AGENTS_ORDER}
            status[AGENTS_ORDER[0]] = "working"
            render_status(placeholders, status)

            result_holder = {"output": None, "error": None}

            def on_task_complete(task_output):
                role = getattr(task_output, "agent", None)
                if role in status:
                    status[role] = "done"
                    idx = AGENTS_ORDER.index(role)
                    if idx + 1 < len(AGENTS_ORDER):
                        status[AGENTS_ORDER[idx + 1]] = "working"

            def worker():
                try:
                    result_holder["output"] = run_crew(topic, task_callback=on_task_complete)
                except Exception as e:
                    result_holder["error"] = str(e)

            thread = Thread(target=worker)
            thread.start()

            while thread.is_alive():
                render_status(placeholders, status)
                time.sleep(1)
            thread.join()
            render_status(placeholders, status)

            if result_holder["error"]:
                st.error(f"Something went wrong: {result_holder['error']}")
            else:
                chat_id = str(uuid.uuid4())
                st.session_state.chats[chat_id] = {
                    "topic": topic,
                    "article": result_holder["output"],
                }
                st.session_state.active_chat_id = chat_id
                st.rerun()
else:
    chat = st.session_state.chats[st.session_state.active_chat_id]
    st.subheader(f"Topic: {chat['topic']}")
    st.markdown("---")
    st.markdown(chat["article"])
