import streamlit as st
from google import genai
from google.genai import types

# -----------------------------------
# 페이지 설정
# -----------------------------------
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💌",
    layout="centered"
)

st.title("💌 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반 상담 챗봇")

# -----------------------------------
# API KEY 불러오기
# -----------------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("secrets.toml에 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

# -----------------------------------
# Gemini Client 생성
# -----------------------------------
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 클라이언트 생성 오류: {e}")
    st.stop()

# -----------------------------------
# 시스템 프롬프트
# -----------------------------------
SYSTEM_PROMPT = """
너는 공감 능력이 뛰어난 연애상담 AI 챗봇이다.

규칙:
- 사용자의 감정을 공감해라.
- 너무 공격적이거나 단정적으로 말하지 마라.
- 현실적인 조언을 제공해라.
- 짧지만 따뜻하게 답변해라.
- 위험하거나 극단적인 상황은 전문가 상담을 권장해라.
"""

# -----------------------------------
# 세션 상태 초기화
# -----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------
# 이전 채팅 출력
# -----------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------
# 사용자 입력
# -----------------------------------
user_input = st.chat_input("고민을 편하게 이야기해보세요...")

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답 생성
    with st.chat_message("assistant"):

        with st.spinner("답변 생성 중..."):

            try:
                # 대화 기록 구성
                history_text = ""

                for msg in st.session_state.messages:
                    role = "사용자" if msg["role"] == "user" else "AI"
                    history_text += f"{role}: {msg['content']}\n"

                full_prompt = f"""
{SYSTEM_PROMPT}

다음은 이전 대화 내용이다.

{history_text}

AI:
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=500,
                    )
                )

                bot_reply = response.text

                # 응답 출력
                st.markdown(bot_reply)

                # 세션 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_reply
                })

            except Exception as e:
                error_message = f"오류가 발생했습니다: {e}"

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
