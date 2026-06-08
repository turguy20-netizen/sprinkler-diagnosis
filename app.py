import streamlit as st
import google.generativeai as genai
from PIL import Image
import openpyxl
import io

st.set_page_config(page_title="엑셀 이미지 일괄 진단", layout="wide")
st.title("📊 엑셀 시트 이미지 일괄 진단 AI")
st.write("사진이 포함된 엑셀 파일(.xlsx)을 올리면, AI가 시트 내의 모든 사진을 찾아내어 분석합니다.")

# 1. Gemini 2.5 Flash API 설정 (Secrets 안전 유지)
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. 엑셀 파일 업로더
uploaded_file = st.file_uploader("이미지가 포함된 엑셀 파일을 업로드하세요...", type=["xlsx"])

if uploaded_file:
    if st.button("🚀 엑셀 이미지 전체 분석 시작"):
        try:
            # openpyxl로 엑셀 파일 로드
            wb = openpyxl.load_workbook(uploaded_file)
            image_count = 0
           
            # 모든 시트를 순회하며 이미지 찾기
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
               
                # 시트 내에 이미지가 존재하는지 확인
                if hasattr(ws, '_images') and ws._images:
                    st.write(f"---")
                    st.subheader(f"📋 시트명: {sheet_name}")
                   
                    for idx, excel_image in enumerate(ws._images):
                        image_count += 1
                       
                        # 엑셀 내부의 이미지 바이너리 추출 및 PIL 이미지 변환
                        img_bytes = excel_image._data()
                        img = Image.open(io.BytesIO(img_bytes))
                       
                        # 화면에 이쁘게 배치하기 (좌측 사진, 우측 AI 리포트)
                        # anchor 속성을 통해 사진이 위치한 대략적인 셀 위치(예: E5)를 파악합니다.
                        cell_loc = excel_image.anchor if hasattr(excel_image, 'anchor') else "위치 불명"
                       
                        with st.expander(f"🔍 사진 #{image_count} (엑셀 내 위치: {cell_loc})", expanded=True):
                            col1, col2 = st.columns([1, 2])
                           
                            with col1:
                                st.image(img, caption=f"추출된 이미지 #{image_count}", use_container_width=True)
                               
                            with col2:
                                with st.spinner('Gemini 2.5 Flash가 사진을 판독 중입니다...'):
                                    try:
                                        prompt = "현장 안전 점검 전문가로서 이 스프링클러 사진의 부식 상태를 (정상/주의/심각)으로 진단하고 상세 이유와 조치 방법을 한글로 간결하게 번호 붙여서 설명해줘."
                                        response = model.generate_content([prompt, img])
                                        st.markdown(response.text)
                                    except Exception as ai_err:
                                        st.error(f"AI 분석 중 오류: {ai_err}")
                                       
            if image_count == 0:
                st.warning("⚠️ 엑셀 파일 안에서 이미지를 찾지 못했습니다. 사진이 셀 위에 정상적으로 삽입되어 있는지 확인해 주세요.")
            else:
                st.success(f"🎉 성공적으로 총 {image_count}장의 사진을 추출하여 분석을 마쳤습니다!")
               
        except Exception as e:
            st.error(f"🚨 엑셀 파일을 읽는 중 오류가 발생했습니다. 파일이 손상되었거나 호환되지 않는 포맷일 수 있습니다: {e}")

