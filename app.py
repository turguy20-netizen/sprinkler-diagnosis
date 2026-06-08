import streamlit as st
import google.generativeai as genai
from PIL import Image
import zipfile
import io
import time  # 무료 요금제 속도 제한(Rate Limit) 방지용

st.set_page_config(page_title="엑셀 이미지 일괄 진단", layout="wide")
st.title("🚀 엑셀 숨은 이미지 직접 추출 & 진단 AI")
st.write("엑셀 파일 내부 구조를 직접 분해하여, 숨겨진 원본 이미지만을 강제로 추출해 분석합니다.")

# 1. Gemini 2.5 Flash API 설정 (Secrets 안전 유지)
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. 엑셀 파일 업로더
uploaded_file = st.file_uploader("이미지가 포함된 엑셀 파일(.xlsx)을 업로드하세요...", type=["xlsx"])

if uploaded_file:
    if st.button("🚀 엑셀 이미지 강제 추출 및 전체 분석"):
        try:
            image_count = 0
           
            # [핵심 기술] 엑셀(.xlsx) 파일을 압축 파일(ZIP)로 취급하여 직접 엽니다.
            with zipfile.ZipFile(uploaded_file, 'r') as excel_zip:
                # 엑셀 내부의 모든 파일 목록 가져오기
                file_list = excel_zip.namelist()
               
                # 'xl/media/' 폴더 안에 있는 실제 이미지 파일(jpg, png 등)만 필터링
                image_files = [f for f in file_list if f.startswith('xl/media/') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
               
                if not image_files:
                    st.warning("⚠️ 엑셀 파일 내부에 추출할 수 있는 이미지(jpg, png)가 없습니다.")
                else:
                    st.success(f"✅ 에러 우회 성공! 총 {len(image_files)}장의 이미지를 찾아냈습니다. 분석을 시작합니다.")
                    st.write("---")
                   
                    for img_path in image_files:
                        image_count += 1
                       
                        # 압축 파일 내에서 이미지 데이터만 쏙 빼오기
                        img_bytes = excel_zip.read(img_path)
                        img = Image.open(io.BytesIO(img_bytes))
                       
                        with st.expander(f"🔍 추출된 사진 #{image_count}", expanded=True):
                            col1, col2 = st.columns([1, 2])
                           
                            with col1:
                                st.image(img, use_container_width=True)
                               
                            with col2:
                                with st.spinner('Gemini 2.5 Flash가 판독 중입니다... (무료 요금제 제한으로 15초 대기)'):
                                    try:
                                        prompt = "현장 안전 점검 전문가로서 이 스프링클러 사진의 부식 상태를 (정상/주의/심각)으로 진단하고 상세 이유와 조치 방법을 한글로 간결하게 번호 붙여서 설명해줘."
                                        response = model.generate_content([prompt, img])
                                        st.markdown(response.text)
                                       
                                        # [핵심 추가] 1분에 5장 제한을 피하기 위해 한 장 분석 후 15초 멈춤
                                        time.sleep(15)
                                       
                                    except Exception as ai_err:
                                        st.error(f"AI 분석 중 오류: {ai_err}")

        except zipfile.BadZipFile:
            st.error("🚨 올바른 엑셀(.xlsx) 파일이 아니거나 강력한 사내 보안(DRM)으로 압축이 잠겨 있습니다.")
        except Exception as e:
            st.error(f"🚨 예상치 못한 오류가 발생했습니다: {e}")
