import streamlit as st
import tempfile
import os
import subprocess

st.set_page_config(page_title="MP4 to WebP 일괄 변환기", page_icon="🎬", layout="centered")

st.title("🎬 MP4 ➔ WebP 일괄 변환기")
st.write("여러 MP4 파일을 올리고 변환 후 각각 개별 다운로드하세요!")

# 세션 상태 초기화 (다운로드 시 화면 리셋 방지용)
if "converted_files" not in st.session_state:
    st.session_state.converted_files = []

# 여러 파일 선택 지원
uploaded_files = st.file_uploader(
    "변환할 MP4 파일들을 선택하거나 드래그하세요 (여러 개 선택 가능)", 
    type=["mp4"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📁 총 {len(uploaded_files)}개의 파일이 선택되었습니다.")
    
    if st.button("🚀 전체 파일 WebP로 변환 시작", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        temp_dir = tempfile.mkdtemp()
        st.session_state.converted_files = []  # 기존 저장 결과 초기화

        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"⏳ [{idx + 1}/{len(uploaded_files)}] 변환 중: {uploaded_file.name}")
            
            tmp_input_path = os.path.join(temp_dir, uploaded_file.name)
            with open(tmp_input_path, "wb") as f:
                f.write(uploaded_file.read())

            output_name = os.path.splitext(uploaded_file.name)[0] + ".webp"
            output_path = os.path.join(temp_dir, output_name)

            try:
                cmd = [
                    'ffmpeg',
                    '-y',
                    '-i', tmp_input_path,
                    '-vcodec', 'libwebp',
                    '-filter:v', 'fps=fps=min(source_fps\,30)',
                    '-lossless', '0',
                    '-q:v', '53',
                    '-preset', 'default',
                    '-loop', '0',
                    output_path
                ]
                
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    with open(output_path, "rb") as f:
                        file_bytes = f.read()
                    file_size_mb = round(len(file_bytes) / (1024 * 1024), 2)
                    # 세션 상태에 데이터 보관
                    st.session_state.converted_files.append((output_name, file_bytes, file_size_mb))

            except Exception as e:
                st.error(f"❌ {uploaded_file.name} 변환 실패: {e}")

            progress_bar.progress((idx + 1) / len(uploaded_files))

        status_text.empty()
        progress_bar.empty()

# 변환된 파일 목록이 세션에 존재하면 화면에 계속 유지
if st.session_state.converted_files:
    st.success(f"🎉 총 {len(st.session_state.converted_files)}개 파일 변환 완료!")
    st.markdown("---")
    st.subheader("📥 개별 다운로드 목록")

    for idx, (file_name, file_bytes, file_size_mb) in enumerate(st.session_state.converted_files):
        st.write(f"**{idx + 1}. {file_name}** ({file_size_mb} MB)")
        st.download_button(
            label=f"📥 {file_name} 다운로드",
            data=file_bytes,
            file_name=file_name,
            mime="image/webp",
            key=f"download_{idx}_{file_name}",
            use_container_width=True
        )
