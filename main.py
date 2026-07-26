

import traceback
from tools_schema import tools
from config import GMAIL_USER ,GMAIL_APP_PASSWORD ,BOT_TOKEN ,CHAT_ID ,GROQ_API_KEY ,MODEL_PATH ,MODEL_NAME 
from llm import device ,tokenizer ,model
from llm_service import llm
from email_process import *
from state import AgentState
from agent import Agent

"""# chạy agent"""

abot = Agent(llm, tools, system=prompt)

email_ids = get_unseen_email_ids()

#print(f"Tìm thấy {len(email_ids)} email chưa đọc")

for email_id in email_ids:

    try:

        email_data = load_email(email_id)

        print("load email ing")

        initial_state = {
            **email_data,
            "messages": []
        }

        for event in abot.graph.stream(
            initial_state,
            {
                "configurable": {
                    "thread_id": email_id.decode()
                }
            }
        ):
            print(event)

        #print(f"Đã xử lý email {email_id.decode()}" )

    except Exception:
        traceback.print_exc()