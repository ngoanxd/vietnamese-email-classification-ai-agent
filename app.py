import streamlit as st
import traceback
import time

# Import các thành phần từ dự án của bạn
from tools_schema import tools
from llm import device, tokenizer, model
from llm_service import llm
from email_process import get_unseen_email_ids, load_email
from agent import Agent
from config import prompt

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="AI Email Automation Agent", 
    page_icon="🤖", 
    layout="wide", # Chuyển sang chế độ màn hình rộng cho chuyên nghiệp
    initial_sidebar_state="expanded"
)

# --- THAY ĐỔI GIAO DIỆN BẰNG CSS CUSTOM (Tối ưu khoảng cách & Font) ---
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1E3A8A; font-weight: 800; }
    .stAlert p { font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- THANH MENU BÊN TRÁI (SIDEBAR) - NƠI NHẬP CẤU HÌNH ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
    st.title("⚙️ Hệ Thống Cấu Hình")
    st.write("Vui lòng điền thông tin tài khoản của bạn để kết nối với AI Agent.")
    st.markdown("---")
    
    # Các ô nhập liệu gọn gàng bên thanh Menu
    gmail_user = st.text_input("📬 Địa chỉ Gmail", placeholder="example@gmail.com")
    gmail_app_password = st.text_input("🔑 Gmail App Password", type="password", placeholder="xxxx xxxx xxxx xxxx")
    bot_token = st.text_input("🤖 Telegram Bot Token", type="password", placeholder="8588049561:AA...")
    chat_id = st.text_input("🆔 Telegram Chat ID", placeholder="8958339753")
    
    st.markdown("---")
    # Nút kích hoạt nổi bật
    submit_button = st.button("🚀 KÍCH HOẠT AGENT", use_container_width=True, type="primary")

# --- KHÔNG GIAN CHÍNH (MAIN CONTENT) ---
st.title("🤖 Smart AI Email Assistant")
st.caption("Hệ thống tự động quét, tóm tắt và soạn thảo thư phản hồi thông minh thông qua Telegram.")

# Hiển thị hướng dẫn ban đầu nếu chưa bấm nút kích hoạt
if not submit_button:
    st.info("💡 **Hướng dẫn nhanh:** Hãy nhập đầy đủ thông tin cấu hình ở **Thanh Menu bên trái** và nhấn **Kích hoạt Agent** để bắt đầu quét Email chưa đọc.")

# --- LOGIC XỬ LÝ KHI NGƯỜI DÙNG BẤM NÚT ---
# --- LOGIC XỬ LÝ KHI NGƯỜI DÙNG BẤM NÚT ---
if submit_button:
    if not (gmail_user and gmail_app_password and bot_token and chat_id):
        st.error("❌ **Thiếu thông tin:** Vui lòng kiểm tra và điền đầy đủ các trường cấu hình ở thanh Menu bên trái!")
    else:
        # Ghi đè cấu hình động vào hệ thống
        import config
        config.GMAIL_USER = gmail_user
        config.GMAIL_APP_PASSWORD = gmail_app_password
        config.BOT_TOKEN = bot_token
        config.CHAT_ID = chat_id

        # Hiệu ứng Spinner cao cấp lúc khởi tạo hệ thống
        with st.spinner("⏳ Đang kết nối máy chủ và khởi tạo bộ não AI..."):
            try:
                abot = Agent(llm, tools, system=prompt)
                email_ids = get_unseen_email_ids()
                time.sleep(1)  # Tạo độ trễ mượt mà cho UI
            except Exception as system_error:
                st.error(f"🚨 **Lỗi kết nối hệ thống:** Không thể kết nối IMAP/Telegram. Vui lòng kiểm tra lại tài khoản! Chi tiết: {str(system_error)}")
                st.stop()

        # Kiểm tra danh sách thư chưa đọc
        if not email_ids:
            st.toast("📭 Hộp thư sạch sẽ!", icon="🎉")
            st.success("🎉 **Tuyệt vời! Không có email nào chưa đọc trong hộp thư của bạn.**")
        else:
            st.toast(f"📬 Tìm thấy {len(email_ids)} email mới!", icon="🔔")
            st.subheader(f"📊 Tiến Trình Xử Lý Hàng Đợi ({len(email_ids)} Thư Chưa Đọc)", divider="blue")
            
            # Vòng lặp duyệt qua từng Email một cách khoa học
            for idx, email_id in enumerate(email_ids):
                try:
                    email_data = load_email(email_id)
                    
                    # Đóng gói thông tin Email vào các Card (st.expander) cực đẹp
                    with st.expander(f"✉️ **Thư số {idx+1}:** {email_data['tieude']} (Từ: {email_data['dc']})", expanded=True):
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown(f"**👤 Người gửi:** `{email_data.get('name', 'Không rõ')}`")
                            st.markdown(f"**📧 Địa chỉ:** `{email_data.get('dc', '')}`")
                        with col2:
                            st.markdown(f"**📌 Tiêu đề chính:** *{email_data.get('tieude', '(Không có tiêu đề)')}*")
                        
                        st.markdown("**📄 Bản xem trước nội dung gốc:**")
                        st.caption(email_data['nd'][:250] + "..." if len(email_data['nd']) > 250 else email_data['nd'])
                        st.markdown("---")
                        
                        # --- HỘP TRẠNG THÁI ĐỘNG THẾ HỆ MỚI (ST.STATUS) ---
                        # Vừa sửa lỗi missing argument 'input' vừa dọn sạch log hệ thống loằng ngoằng
                        with st.status("🤖 AI Agent đang khởi động luồng phân tích...", expanded=True) as status:
                            
                            initial_state = {
                                **email_data,
                                "messages": []
                            }
                            
                            # GỌI HÀM STREAM CHUẨN ĐÚNG PHIÊN BẢN LANGGRAPH MỚI (Đã sửa lỗi input)
                            for event in abot.graph.stream(
                                input=initial_state,
                                config={"configurable": {"thread_id": email_id.decode()}}
                            ):
                                # Trích xuất và phân tích trạng thái từ các node để sinh thông báo tiếng Việt mượt mà
                                for node_name, node_data in event.items():
                                    if node_name == "classify_email":
                                        status.update(label="🔍 Đang quét cấu trúc và định tuyến phân loại Email...", state="running")
                                    elif node_name == "llm":
                                        status.update(label="🧠 Bộ não AI đang suy nghĩ chiến lược phản hồi...", state="running")
                                    elif node_name == "excute_action":
                                        if 'write_email_rely' in node_data:
                                            status.update(label="📝 Đã soạn thảo xong bức thư phản hồi nháp!", state="running")
                                    elif node_name == "send_telegram":
                                        status.update(label="📲 Đã đẩy bản dịch tóm tắt lên Telegram của bạn thành công!", state="running")
                                    elif node_name == "get_human_review":
                                        # Trạng thái chờ người dùng phê duyệt trên điện thoại
                                        status.update(label="⏳ Đang chờ bạn ấn 'Phê duyệt' hoặc phản hồi qua Telegram (Hạn định 30 giây)...", state="running")
                                        if node_data.get('next_step') == 'END' and "Người dùng im lặng" in str(node_data.get('messages','')):
                                            status.update(label="⏰ Quá 30 giây bạn không phản hồi. Hệ thống tự động HỦY quy trình thư này.", state="error")
                                    elif node_name == "send_email":
                                        status.update(label="🚀 Bạn đã duyệt! Đang thực hiện gửi email phản hồi chính thức...", state="running")
                            
                            # Đánh dấu hoàn thành an toàn cho luồng graph của email hiện tại
                            status.update(label="✅ Hoàn thành phân tích và đóng luồng làm việc thành công!", state="complete")
                        
                        # Thông báo thành công riêng cho từng mail
                        st.success(f"✔️ Đã xử lý xong trọn vẹn quy trình cho email từ **{email_data['dc']}**")
                        
                except Exception as e:
                    st.error(f"❌ **Lỗi cục bộ xảy ra tại thư này:** {str(e)}")
                    traceback.print_exc()
            
            # Hiệu ứng thả bóng bay chúc mừng rực rỡ khi kết thúc tất cả emails trong danh sách
            st.balloons()