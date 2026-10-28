import streamlit as st
from PIL import Image
from io import BytesIO
import io
import json
import requests
from pathlib import Path
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api").rstrip("/")

def process_with_api(image, mode="smart", noise_level="Nhẹ", contrast=False, binarize=False,
                     apply_filter=False, filter_method="median", filter_level="nhe",
                     apply_opening=False, apply_closing=False, apply_erosion=False, apply_dilation=False):
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    buffer.seek(0)
    files = {"file": ("scan.png", buffer, "image/png")}
    levels = {"Nhẹ": "nhe", "Vừa": "vua", "Mạnh": "manh"}
    data = {
        "mode": mode,
        "level": levels[noise_level],
        "contrast": str(contrast).lower(),
        "binarize": str(binarize).lower(),
        "apply_filter": str(apply_filter).lower(),
        "filter_method": filter_method,
        "filter_level": filter_level,
        "apply_erosion": str(apply_erosion).lower(),
        "apply_dilation": str(apply_dilation).lower(),
        "apply_opening": str(apply_opening).lower(),
        "apply_closing": str(apply_closing).lower(),
    }
    response = requests.post(
        f"{API_URL}/enhance-with-options", files=files, data=data, timeout=120
    )
    response.raise_for_status()
    processed = Image.open(io.BytesIO(response.content)).copy()
    metadata = json.loads(response.headers.get("X-Processing-Metadata", "{}"))
    return processed, metadata

st.set_page_config(
    page_title="ScanCare | Nâng cao chất lượng tài liệu",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ====================== SESSION STATE ======================
if "page" not in st.session_state:
    st.session_state.page = "upload"  # "upload" hoặc "result"

if "smart_enabled" not in st.session_state:
    st.session_state.smart_enabled = True
if "apply_filter" not in st.session_state:
    st.session_state.apply_filter = False
if "filter_method" not in st.session_state:
    st.session_state.filter_method = "median"
if "filter_level" not in st.session_state:
    st.session_state.filter_level = "nhe"

if "processing_metadata" not in st.session_state:
    st.session_state.processing_metadata = {}

if "enhance_contrast" not in st.session_state:
    st.session_state.enhance_contrast = True
if "binarize" not in st.session_state:
    st.session_state.binarize = False
if "apply_erosion" not in st.session_state:
    st.session_state.apply_erosion = False
if "apply_dilation" not in st.session_state:
    st.session_state.apply_dilation = False
if "apply_opening" not in st.session_state:
    st.session_state.apply_opening = False
if "apply_closing" not in st.session_state:
    st.session_state.apply_closing = False

if "noise_level" not in st.session_state:
    st.session_state.noise_level = "Vừa"

if "image_original" not in st.session_state:
    st.session_state.image_original = None

if "image_processed" not in st.session_state:
    st.session_state.image_processed = None

if "file_name" not in st.session_state:
    st.session_state.file_name = "scancare_result.png"


# Xử lý tài liệu thực tế được thực hiện bởi FastAPI qua process_with_api().



def run_api_processing():
    """Xu ly lai tu anh goc, khong cong don len ket qua cu."""
    mode = "smart" if st.session_state.smart_enabled else "none"
    try:
        with st.spinner("Đang xử lý ảnh bằng FastAPI..."):
            output, metadata = process_with_api(
                st.session_state.image_original,
                mode=mode,
                noise_level=st.session_state.noise_level,
                contrast=st.session_state.enhance_contrast,
                binarize=st.session_state.binarize,
                apply_filter=st.session_state.apply_filter,
                filter_method=st.session_state.filter_method,
                filter_level=st.session_state.filter_level,
                apply_erosion=st.session_state.apply_erosion,
                apply_dilation=st.session_state.apply_dilation,
                apply_opening=st.session_state.apply_opening,
                apply_closing=st.session_state.apply_closing,
            )
    except requests.exceptions.RequestException as exc:
        st.error(f"Không kết nối được FastAPI hoặc API trả lỗi: {exc}")
        return False
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        st.error(f"Không đọc được kết quả xử lý: {exc}")
        return False
    st.session_state.image_processed = output
    st.session_state.processing_metadata = metadata
    return True


def image_to_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# Các tùy chọn dùng chung cho trang upload và trang xử lý lại.
def render_processing_controls(suffix):
    st.session_state.smart_enabled = st.checkbox(
        "Tự động hiệu chỉnh nền (Smart Enhance)",
        value=st.session_state.smart_enabled,
        key=f"smart_{suffix}",
    )
    st.caption(
        "Nên bật khi nền giấy loang sáng hoặc bị xám. Tự phân tích và hiệu "
        "chỉnh nền nếu cần; có thể chuyển ảnh màu thành ảnh xám, không thay "
        "thế bộ lọc khử nhiễu."
    )

    st.session_state.apply_filter = st.checkbox(
        "Bật lọc nhiễu",
        value=st.session_state.apply_filter,
        key=f"filter_enabled_{suffix}",
    )
    st.caption(
        "Bật khi ảnh có hạt nhiễu hoặc đốm nhỏ. Nếu ảnh đã sạch, hãy tắt để "
        "tránh làm mềm nét chữ."
    )
    if st.session_state.apply_filter:
        st.session_state.filter_method = st.radio(
            "Thuật toán lọc",
            ["median", "gaussian"],
            format_func=lambda x: "Median Filter" if x == "median" else "Gaussian Filter",
            index=["median", "gaussian"].index(st.session_state.filter_method),
            horizontal=True,
            key=f"filter_method_{suffix}",
        )
        if st.session_state.filter_method == "median":
            st.caption(
                "Median: phù hợp với đốm đen/trắng kiểu muối tiêu; thường giữ "
                "biên chữ tốt hơn Gaussian."
            )
        else:
            st.caption(
                "Gaussian: làm mượt nhiễu hạt nhẹ; có thể làm mềm biên và mờ "
                "nét chữ hơn Median."
            )
        levels = ["nhe", "vua", "manh"]
        st.session_state.filter_level = st.radio(
            "Mức độ lọc",
            levels,
            format_func=lambda x: {"nhe": "Nhẹ (3×3)", "vua": "Vừa (5×5)", "manh": "Mạnh (7×7)"}[x],
            index=levels.index(st.session_state.filter_level),
            horizontal=True,
            key=f"filter_level_{suffix}",
        )
        level_descriptions = {
            "nhe": "Nhẹ 3×3: nên thử đầu tiên; giữ chi tiết chữ tốt nhất.",
            "vua": "Vừa 5×5: dùng khi nhiễu rõ hơn; kiểm tra chữ nhỏ sau xử lý.",
            "manh": "Mạnh 7×7: dùng khi nhiễu nhiều; dễ làm mờ hoặc mất nét mảnh.",
        }
        st.caption(level_descriptions[st.session_state.filter_level])

    st.markdown("**Tùy chọn nâng cao:**")
    st.session_state.enhance_contrast = st.checkbox(
        "Tăng độ tương phản",
        value=st.session_state.enhance_contrast,
        key=f"contrast_{suffix}",
    )
    st.caption(
        "Bật khi chữ nhạt hoặc nền xám để tăng chênh lệch sáng-tối. Kết quả "
        "chuyển sang ảnh xám; có thể làm ảnh tương phản mạnh trông gắt hơn."
    )
    st.session_state.binarize = st.checkbox(
        "Làm rõ chữ bằng nhị phân hóa (Đen / Trắng)",
        value=st.session_state.binarize,
        key=f"binarize_{suffix}",
    )
    st.caption(
        "Bật cho tài liệu chủ yếu là chữ đen trên giấy sáng để tạo ảnh đen "
        "trắng. Không phù hợp với con dấu, ảnh hoặc nội dung cần giữ màu."
    )
    if st.session_state.binarize:
        st.caption(
            "Ngưỡng thích nghi xử lý nền sáng không đều tốt hơn ngưỡng cố "
            "định, nhưng chữ mờ vẫn có thể bị mất."
        )
        st.markdown("**Các phép hình thái học (tùy chọn):**")
        st.caption("Chỉ áp dụng trên ảnh đã nhị phân hóa. Nên bật từng phép một để so sánh; kernel 3×3 có thể ảnh hưởng dấu và nét chữ nhỏ.")
        st.session_state.apply_erosion = st.checkbox(
            "Erosion (phép co) — làm mảnh nét chữ",
            value=st.session_state.apply_erosion,
            key=f"erosion_{suffix}",
        )
        st.caption("Dùng thử khi nét chữ quá dày hoặc dính nhẹ; có nguy cơ xóa nét mảnh và dấu tiếng Việt.")
        st.session_state.apply_dilation = st.checkbox(
            "Dilation (phép giãn) — làm dày nét chữ",
            value=st.session_state.apply_dilation,
            key=f"dilation_{suffix}",
        )
        st.caption("Dùng thử khi nét chữ quá mảnh hoặc đứt nhẹ; có nguy cơ làm dính các ký tự gần nhau.")
        st.session_state.apply_opening = st.checkbox(
            "Opening — loại đốm nhỏ",
            value=st.session_state.apply_opening,
            key=f"opening_{suffix}",
        )
        st.caption(
            "Nên bật khi còn nhiều chấm nhiễu nhỏ. Có thể xóa nét chữ mảnh; "
            "nếu chữ bị rỗ, hãy tắt."
        )
        st.session_state.apply_closing = st.checkbox(
            "Closing — nối khe nhỏ",
            value=st.session_state.apply_closing,
            key=f"closing_{suffix}",
        )
        st.caption(
            "Nên bật khi nét chữ có khe đứt nhỏ. Có thể làm chữ dày hoặc "
            "dính nét nếu áp dụng quá mức."
        )


# ====================== STYLESHEET (CSS) ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

:root {
    --red: #c83e3e;
    --red-dark: #a92f2f;
    --red-light: #fff5f5;
    --ink: #1f2937;
    --muted: #6b7280;
    --border: #e5e7eb;
    --surface: #ffffff;
    --bg: #f8fafc;
}

html, body, [class*="css"], input, button, textarea, [data-testid="stMarkdownContainer"] {
    font-family: 'Be Vietnam Pro', 'Segoe UI', Roboto, sans-serif !important;
}

.stApp {
    background: var(--bg);
    color: var(--ink);
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 1300px;
    padding: 18px 24px 12px !important;
}

/* Header thương hiệu */
.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}

.brand-icon {
    width: 44px;
    height: 44px;
    background: var(--red);
    color: white;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: 800;
    box-shadow: 0 4px 10px rgba(200, 62, 62, 0.2);
}

.brand-name {
    font-size: 24px;
    font-weight: 800;
    color: var(--ink);
    line-height: 1.2;
}

.brand-subtitle {
    color: var(--muted);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    margin-top: 2px;
}

/* Tiêu đề mục */
.section-heading {
    font-size: 20px;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 4px;
}

.section-description {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 12px;
}

/* Căn giữa cột trái */
.left-col-header {
    text-align: center !important;
}

.left-col-header .section-heading,
.left-col-header .section-description {
    text-align: center !important;
}

/* Khung container nổi */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px 20px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

/* Custom Khung Upload & Căn Giữa Cột */
div[data-testid="stFileUploader"] {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
}

div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploaderDropzone"] {
    background-color: var(--red-light) !important;
    border: 2px dashed #f0a3a3 !important;
    border-radius: 14px !important;
    padding: 24px 16px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    text-align: center !important;
}

div[data-testid="stFileUploaderDropzone"] > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    gap: 10px !important;
    width: 100% !important;
}

/* NÚT UPLOAD - MÀU ĐỎ CHỦ ĐẠO & CĂN GIỮA */
div[data-testid="stFileUploaderDropzone"] button,
div[data-testid="stFileUploaderDropzone"] [data-testid*="Button"],
div[data-testid="stFileUploader"] button {
    background-color: var(--red) !important;
    background: var(--red) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 8px 28px !important;
    margin: 0 auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 6px rgba(200, 62, 62, 0.25) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stFileUploaderDropzone"] button:hover,
div[data-testid="stFileUploaderDropzone"] [data-testid*="Button"]:hover,
div[data-testid="stFileUploader"] button:hover {
    background-color: var(--red-dark) !important;
    background: var(--red-dark) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 10px rgba(169, 47, 47, 0.35) !important;
    cursor: pointer !important;
}

div[data-testid="stFileUploaderDropzone"] button *,
div[data-testid="stFileUploaderDropzone"] [data-testid*="Button"] * {
    color: #ffffff !important;
}

/* Chú thích phía dưới uploader */
.upload-caption-note {
    color: var(--muted);
    font-size: 13px;
    margin-top: 14px;
    text-align: center;
    font-weight: 500;
}

/* Radio button & Checkbox label */
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] p,
div[data-testid="stWidgetLabel"] p {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
}

div[data-testid="stCheckbox"] label p {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
}

/* Ghi chú hướng dẫn tùy chọn nâng cao */
.user-note {
    background: #f8fafc;
    border-left: 3px solid var(--red);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    color: #334155;
    line-height: 1.5;
    margin: 4px 0 12px 24px;
}

/* Dynamic Tip Box */
.tip-box {
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.5;
    margin: 8px 0 14px;
    transition: all 0.3s ease;
}

/* Nút bấm chung */
div.stButton > button,
div[data-testid="stDownloadButton"] button {
    background: var(--red) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    min-height: 42px !important;
    box-shadow: 0 3px 8px rgba(200, 62, 62, 0.2) !important;
}

div.stButton > button:hover,
div[data-testid="stDownloadButton"] button:hover {
    background: var(--red-dark) !important;
}

.preview-label {
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 8px;
}

.custom-divider {
    height: 1px;
    background-color: var(--border);
    margin: 16px 0;
}

.footer {
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    padding: 20px 0 6px;
}
</style>
""", unsafe_allow_html=True)


# ====================== HEADER ======================
st.markdown("""
<div class="brand">
    <div class="brand-icon">S</div>
    <div>
        <div class="brand-name">ScanCare</div>
        <div class="brand-subtitle">SCAN DOCUMENT ENHANCEMENT</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ====================== TRANG 1: TẢI ẢNH & TÙY CHỌN ======================
if st.session_state.page == "upload":
    upload_col, options_col = st.columns([1.05, 0.95], gap="medium")

    with upload_col:
        st.markdown(
            '<div class="left-col-header">'
            '<div class="section-heading">01. Tải tài liệu lên</div>'
            '<div class="section-description">Chọn ảnh scan hoặc ảnh chụp cần cải thiện</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            uploaded_file = st.file_uploader(
                "Chọn ảnh",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
                help="Hỗ trợ JPG, JPEG và PNG.",
            )

            if uploaded_file is not None:
                try:
                    img = Image.open(uploaded_file).convert("RGB")
                    st.session_state.image_original = img
                    st.session_state.file_name = uploaded_file.name

                    st.image(img, use_container_width=True)
                    st.caption(f"Ảnh đã chọn: {uploaded_file.name} | Kích thước: {img.size[0]} × {img.size[1]} px")
                except Exception:
                    st.session_state.image_original = None
                    st.error("Không thể đọc ảnh này. Vui lòng chọn ảnh JPG hoặc PNG khác.")
            else:
                st.session_state.image_original = None
                st.markdown(
                    '<div class="upload-caption-note">Vui lòng tải ảnh tài liệu lên để bắt đầu.</div>',
                    unsafe_allow_html=True,
                )

    with options_col:
        st.markdown(
            '<div class="section-heading">02. Tùy chọn xử lý</div>'
            '<div class="section-description">Chọn mức độ phù hợp với tình trạng tài liệu</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            render_processing_controls("upload")

            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            btn_process = st.button(
                "Nâng cao chất lượng tài liệu",
                use_container_width=True,
                disabled=st.session_state.image_original is None,
            )

            if btn_process and st.session_state.image_original is not None:
                if run_api_processing():
                    st.session_state.page = "result"
                    st.rerun()


# ====================== TRANG 2: TRANG KẾT QUẢ & CẤU HÌNH LẠI ======================
elif st.session_state.page == "result":

    # HÀNG TRÊN CÙNG: Nút "Chọn ảnh khác" ở góc trái + Tiêu đề căn giữa 100%
    top_left, top_center, top_right = st.columns([1.5, 7, 1.5])

    with top_left:
        if st.button("← Chọn ảnh khác"):
            st.session_state.page = "upload"
            st.rerun()

    with top_center:
        st.markdown(
            '<div style="text-align: center; margin-bottom: 12px;">'
            '<div class="section-heading" style="font-size: 22px;">Kết quả nâng cao chất lượng</div>'
            '<div class="section-description" style="margin-bottom: 0;">Đối chiếu trực tiếp giữa ảnh gốc và ảnh đã qua xử lý</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # SO SÁNH 2 ẢNH
    col_orig, col_res = st.columns(2, gap="medium")

    with col_orig:
        st.markdown('<div class="preview-label">Ảnh gốc</div>', unsafe_allow_html=True)
        if st.session_state.image_original is not None:
            st.image(st.session_state.image_original, use_container_width=True)

    with col_res:
        st.markdown('<div class="preview-label">Ảnh đã chỉnh sửa</div>', unsafe_allow_html=True)
        if st.session_state.image_processed is not None:
            st.image(st.session_state.image_processed, use_container_width=True)

            metadata = st.session_state.processing_metadata
            if metadata:
                with st.expander("Thông tin xử lý"):
                    st.json(metadata)

            img_bytes = image_to_bytes(st.session_state.image_processed)
            st.download_button(
                label="Tải ảnh kết quả về máy",
                data=img_bytes,
                file_name=f"enhanced_{Path(st.session_state.file_name).stem}.png",
                mime="image/png",
                use_container_width=True,
            )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # KHUNG ĐIỀU CHỈNH VÀ XỬ LÝ LẠI
    st.markdown(
        '<div class="section-heading">Thay đổi tùy chọn & Xử lý lại</div>'
        '<div class="section-description">Chọn phương pháp và xử lý lại từ ảnh gốc.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        render_processing_controls("result")

        btn_reprocess = st.button("Nâng cao lại chất lượng", use_container_width=True)
        if btn_reprocess and st.session_state.image_original is not None:
            if run_api_processing():
                st.rerun()


# ====================== FOOTER ======================
st.markdown("""
<div class="footer">
    ScanCare | Nâng cao chất lượng tài liệu Scan
</div>
""", unsafe_allow_html=True)