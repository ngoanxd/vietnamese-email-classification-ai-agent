from langgraph.graph import StateGraph, END
import requests
from state import AgentState
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
import torch
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
import time
import config
from llm import*
from llm_service import*

class Agent:

    def __init__(self, model, tools,system=""):
        self.system = system
        graph = StateGraph(AgentState)

        graph.add_node("classify_email",self.classify_email)

        graph.add_node("send_telegram", self.send_telegram)
        graph.add_node("send_email", self.send_email)
        graph.add_node("llm", self.call_openai)
        graph.add_node('get_human_review',self.get_human_review)
        graph.add_node('excute_action',self.excute_action)
        graph.add_node("end", self.end)

        graph.add_edge("end", END)
        graph.add_conditional_edges(
        "classify_email",
         self.router,
         {
            'END':'end',
            'llm':"llm"
        })

        graph.add_conditional_edges(
        "send_telegram",
         self.router,
         {
            'END':'end',
            'get_human_review':"get_human_review"
        })


        graph.add_conditional_edges(
        "get_human_review",
         self.router,
         {
            'END':'end',
            'llm':"llm"
        })

        graph.add_edge("send_email", 'end')


        graph.add_edge("llm", "excute_action")

        graph.add_conditional_edges(
        "excute_action",
        self.router,

        {
            'llm':'llm',
            "send_email":"send_email",
            "get_human_review": "get_human_review",
            "send_telegram": "send_telegram",
            "END": 'end'
        }

)

        graph.set_entry_point("classify_email")
        self.graph = graph.compile()
        self.model = model.bind_tools(tools)


    def classify_email(self, state: AgentState):
       nd=state['nd']
       kq=self.classify_email_bert(nd)
       if kq==1:
         return {
             'next_step':'END'
         }
       else:
        message=HumanMessage(content=f"Tiêu đề: {state['tieude']} \n Nội dung: {state['nd']}")
        return {
             'messages':[message],
             'next_step':'llm'
         }
    #hàm thực thi
    def excute_action(self,state):
      toolcall=state['messages'][-1].tool_calls
      for t in toolcall:
        if t['name']=='classify_rely':
          rely=t['args']['result'].lower()
          message=HumanMessage(content='Tôi muốn tóm tắt email')
          return {'messages':[message],
                  'classify_rely':rely,
                  'next_step':'llm'
                  }

        if t['name']=='summary_email':
          summary=t['args']['message']
          classify_rely=state['classify_rely']

          if classify_rely=='not_rely':
            return {
                'summary_email':summary,
                'next_step':'send_telegram'
            }
          if classify_rely=='rely':
            message=HumanMessage(content='Hãy viết email phản hồi phù với văn phong trong nội dung email write_email_rely')

            return {'messages':[message],
                    'summary_email': summary,
                    'next_step':'llm'
                    }

        if t['name']=='write_email_rely':
          return {
              'write_email_rely':t['args']['message'],
              'header':t['args']['header'],
              'next_step':'send_telegram'
          }

        if t['name']=='classify_human_review':
          kq=t['args']['result'].lower()

          if kq=='no':
            next_step='END'
            return{
                'next_step': next_step        }
          if kq=='yes':
            next_step='send_email'
            return{
                'next_step':  next_step}

          if kq=='more':
            next_step='llm'
            feedback_user=state['feedback_user']
            message=HumanMessage(content=f'Hãy viết email phản hồi theo {feedback_user} ')
            return {'messages':[message],
                  'classify_human_review':kq,
                  'next_step':'llm'
                  }

    def router(self,state: AgentState):
         print('router',state["next_step"])
         return state["next_step"]


    def classify_email_bert(self,email_content: str) -> int:
        """
        Phân loại email spam.

        Args:
            email_content (str): Nội dung email

        Returns:
            int:
                0 -> Không spam
                1 -> Spam
        """

        inputs = tokenizer(
            email_content,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True
        )
        with torch.no_grad():
            outputs = model(**inputs)
            prediction = torch.argmax(outputs.logits, dim=1).item()
        return prediction

    def call_openai(self, state: AgentState):
        messages = state['messages'][-5:]
        print("Độ dài bộ nhớ: ", len(messages))
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def send_telegram(self,state: AgentState):
              
              summary=state['summary_email']
              
              classify_rely=state['classify_rely']

              if classify_rely=='not_rely':
                  total = f"""
                    📋 TÓM TẮT EMAIL

                    {summary}

                    ━━━━━━━━━━━━━━
                    """

              else:
                 write_email_rely= state['write_email_rely']
                 total = (
                "📋 TÓM TẮT EMAIL\n\n"
                f"{summary}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "📧 NỘI DUNG PHẢN HỒI\n\n"
                f"{write_email_rely}"
                """━━━━━━━━━━━━━━━━━━━━\n\n"
                " YES  → Gửi email
                  NO   → Hủy
                  MORE + nội dung → Viết lại email     """
)

              response = requests.post(
                        f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage",
                        json={
                        "chat_id": config.CHAT_ID,
                        "text": total
                    }
                )
              state=response.json()
              if classify_rely=='not_rely':
                return {
                    'next_step':'END'
                }
              else:
                return {
                    'next_step':'get_human_review'
                }

    # lấy thông tin phản hồi từ telegram cuả người dùng
    def get_human_review(self,state: AgentState):

    # Lấy các update mới nhất
      r = requests.get(
          f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates"
      ).json()

      last_update_id = None
      if r["result"]:
          last_update_id = r["result"][-1]["update_id"]

      print("Đang chờ người dùng trả lời...")

      start_time = time.time()

      while time.time() - start_time < 30:  # chờ tối đa 30 giây

          params = {}
          if last_update_id is not None:
              params["offset"] = last_update_id + 1

          r = requests.get(
              f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUpdates",
              params=params
          ).json()

          if r["result"]:
              msg = r["result"][-1]

              last_update_id = msg["update_id"]

              if "message" in msg:
                  text = msg["message"].get("text", "")
                  message=HumanMessage(content=f'Hãy phân loại ý định của người dùng classify_human_review {text}')
                  return {'messages':[message],
                    'feedback_user':text,
                    'next_step':'llm'
                    }

          time.sleep(1)  # kiểm tra mỗi giây

      # Hết 30 giây không có phản hồi
      message=HumanMessage(content='Người dùng im lặng')
      return {
          'messages':[message],
          'next_step':'END'
      }


    def send_email(self,state: AgentState):
      reciver_name=state['name']
      reciver_email=state['dc']
      subject=state['header']
      body=state['write_email_rely']

      msg = MIMEText(body)
      msg["Subject"] = subject
      msg["From"] = GMAIL_USER
      msg["To"] = reciver_email

      with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
          smtp.login(config.GMAIL_USER,config.GMAIL_APP_PASSWORD )
          smtp.send_message(msg)
          message=HumanMessage(content="Gửi email thành công ")
          return {
          'messages':[message],
          'next_step':'END'
      }

    def end (self, state: AgentState):

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
        mail.select("inbox")

        mail.store(
            state["email_id"],
            "+FLAGS",
            "\\Seen"
        )

        mail.logout()

        return {}

