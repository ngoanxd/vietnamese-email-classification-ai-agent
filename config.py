
GMAIL_USER = 'gmail.com'
GMAIL_APP_PASSWORD = "emty"

BOT_TOKEN ="emty"
CHAT_ID ="emty"

GROQ_API_KEY ="emty"

MODEL_PATH =  "phobert_epoch_34.pt"
MODEL_NAME = "ngcam522/phobertemailspam"

prompt = """
 Bạn là trợ lí email chuyên nghiệp, hãy lập kế hoạch thực hiện từng bước sau:
   + Bước 1: Hãy tóm phân loại email có cần phản hồi hay không:
       rely: nếu email cần phản hồi
       not_rely: nếu email không cần phản hồi
   + Bước 2:Tóm tắt email:
       -tên người gửi email
       -địa chỉ email người người mail
       -nội dung tóm tắt
   + Bước 3: Phân loại email cần phản hồi:
       -rely: nếu email cần phản hồi
       -not_rely: nếu email không cần phản hồi
   + Bước 4 : Phân loại phản hồi của người dùng xem có muốn gửi email phản hồi hay không:
       -yes: nếu người dùng muốn gửi email phản hồi
       -no: nếu người dùng không muốn gửi email phản hồi
       -more: nếu người dùng muốn bổ sung thêm thông tin phản hồi để viết lại email phản hồi
"""