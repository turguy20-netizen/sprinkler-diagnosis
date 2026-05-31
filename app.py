import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 페이지 설정
st.set_page_config(page_title="스프링클러 부식 진단 시스템", layout="centered")
st.title("🛡️ 스프링클러 부식 진단 AI")
st.write("현장 사진을 업로드하면 AI 전문가가 부식 상태를 분석합니다.")

# 2. Gemini API 설정
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"] # <--- 여기에 API 키를 넣으세요
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. 사진 업로드 섹션
uploaded_file = st.file_uploader("스프링클러 사진을 선택하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 업로드한 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 이미지', use_container_width=True)
   
    # 분석 버튼
    if st.button("AI 진단 시작"):
        with st.spinner('AI 전문가가 사진을 분석 중입니다...'):
            try:
                # 분석 요청
                prompt = "현장 안전 점검 전문가로서 이 스프링클러의 부식 상태를 (정상/주의/심각)으로 진단하고 상세 이유와 조치 방법을 한글로 알려줘."
                response = model.generate_content([prompt, image])
               
                # 결과 출력
                st.subheader("📋 분석 리포트")
                st.markdown(response.text)
                st.success("분석이 완료되었습니다!")
               
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

# 바닥글
st.divider()
st.caption("본 시스템은 AI 분석 결과이므로 전문가의 최종 확인이 필요합니다.")
