"""
RAG Chatbot - Shopee Help Center

Chatbot trả lời câu hỏi về dịch vụ Shopee dựa trên RAG pipeline.
"""

import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation

load_dotenv()

# === Page Config ===
st.set_page_config(
    page_title="Shopee RAG Chatbot",
    page_icon="🛒",
    layout="wide",
)

# === Session State ===
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = 0


# === Sidebar ===
with st.sidebar:
    st.title("🛒 Shopee RAG Chatbot")
    st.markdown("---")
    st.markdown("### Cài đặt")

    # Top-k slider
    top_k = st.slider(
        "Số chunks tìm kiếm",
        min_value=3,
        max_value=10,
        value=5,
        help="Số lượng documents được dùng để trả lời"
    )

    # Retrieval method
    st.markdown("### Phương pháp retrieval")
    st.caption("- Hybrid: Kết hợp Semantic + BM25")
    st.caption("- PageIndex: Fallback khi score thấp")

    st.markdown("---")

    # Clear chat button
    if st.button("🗑️ Xóa cuộc trò chuyện"):
        st.session_state.messages = []
        st.rerun()

    # Info
    st.markdown("---")
    st.markdown("### Thông tin")
    st.caption("Powered by RAG Pipeline")
    st.caption("Dữ liệu: Shopee Help Center")


# === Helper Functions ===
def _display_sources(sources: list[dict]) -> None:
    """Display sources in expandable format."""
    if not sources:
        return

    with st.expander("📖 Xem chi tiết nguồn", expanded=False):
        for i, source in enumerate(sources, 1):
            metadata = source.get("metadata", {})

            col1, col2 = st.columns([3, 1])

            with col1:
                # Title
                title = metadata.get("title", "Không có tiêu đề")
                st.markdown(f"**{i}. {title}**")

                # URL if available
                url = metadata.get("url")
                if url:
                    st.markdown(f"🔗 [{url}]({url})")

                # Content preview
                content = source.get("content", "")[:300]
                if len(source.get("content", "")) > 300:
                    content += "..."
                st.markdown(f"```\n{content}\n```")

            with col2:
                # Score
                score = source.get("score", 0)
                st.metric("Score", f"{score:.3f}")

                # Retrieval method
                method = source.get("retrieval_method", "unknown")
                st.caption(f"Method: {method}")

            st.markdown("---")


# === Main Content ===
st.title("💬 Shopee RAG Chatbot")
st.markdown("Hỏi tôi về các vấn đề liên quan đến **dịch vụ Shopee**!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            _display_sources(message["sources"])

# === Chat Input ===
query = st.chat_input("Nhập câu hỏi của bạn về Shopee...")

if query:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.chat_message("user"):
        st.markdown(query)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm và tạo câu trả lời..."):
            try:
                result = generate_with_citation(query, top_k=top_k)

                # Display answer
                st.markdown(result["answer"])

                # Display sources
                if result["sources"]:
                    st.markdown("---")
                    st.markdown("**📚 Nguồn tham khảo:**")
                    _display_sources(result["sources"])

                    # Retrieval info
                    retrieval_source = result.get("retrieval_source", "hybrid")
                    method_label = {
                        "dense": "Semantic Search",
                        "bm25": "BM25",
                        "hybrid": "Hybrid (RRF)",
                        "pageindex": "PageIndex"
                    }.get(retrieval_source, retrieval_source)

                    st.caption(f"🔍 Retrieval: {method_label}")

                # Save to session
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                    "retrieval_source": result.get("retrieval_source", "hybrid")
                })

            except Exception as e:
                error_msg = f"Xin lỗi, đã xảy ra lỗi: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })
