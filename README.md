# 🛡️ AI Agent for Vietnamese Email Management

An intelligent AI Agent for Vietnamese email management that combines **Machine Learning**, **PhoBERT**, **Large Language Models (LLMs)** and **LangGraph** to automatically classify spam, summarize emails, generate replies, and assist users through a Human-in-the-Loop workflow.

---

# 🚀 Features

- 📥 Automatically read unread emails from Gmail
- 🛡️ Spam / Not Spam classification using PhoBERT
- 🧠 Email understanding using Llama-3.3-70B
- 📝 Automatic email summarization
- ✉️ Draft professional email replies
- 🤖 LangGraph-based AI Agent workflow
- 👨‍💻 Human-in-the-Loop approval via Telegram
- 📤 Automatically send approved emails

---

# 🏗️ System Architecture

<p align="center">
<img src="images/system_architecture.png" width="900">
</p>

The system consists of four major components:

| Component | Description |
|------------|-------------|
| Spam Classification | PhoBERT-based email classification |
| LLM | Email understanding, summarization and reply generation |
| LangGraph | Workflow orchestration |
| Telegram Bot | Human approval before sending email |

---

# 🔄 AI Agent Workflow

```text
Receive Email
      │
      ▼
Spam Classification
      │
 ┌────┴─────┐
 │          │
Spam     Not Spam
 │          │
 ▼          ▼
End     LLM Analysis
             │
      Need Reply?
      ┌────┴────┐
      │         │
     No        Yes
      │         │
      ▼         ▼
     End   Generate Summary
                 │
          Generate Reply
                 │
          Telegram Review
                 │
       ┌─────────┴─────────┐
       │                   │
   Approve             Modify
       │                   │
       ▼                   ▼
 Send Email        Regenerate Reply
       │
       ▼
      End
```

---

# ⚙️ LangGraph Design

## State

The LangGraph State stores all information shared between Nodes.

```python
State = {
    "email_id": str,
    "sender": str,
    "subject": str,
    "body": str,

    "spam_prediction": int,
    "spam_probability": float,

    "need_reply": bool,
    "summary": str,
    "draft_reply": str,

    "telegram_status": str,
    "user_feedback": str
}
```

---

## Nodes

| Node | Description |
|------|-------------|
| Read Email | Read unread emails from Gmail |
| Spam Classification | Predict Spam / Not Spam |
| LLM Analysis | Analyze email content |
| Generate Summary | Create email summary |
| Generate Reply | Generate draft reply |
| Telegram Review | Send summary and reply to Telegram |
| Human Approval | Wait for user confirmation |
| Send Email | Send email through SMTP |
| End | Finish workflow |

---

## Conditional Edge

The workflow uses conditional routing.

```text
Spam?
├── Yes → End
└── No
      │
Need Reply?
├── No → End
└── Yes
      │
Telegram Decision
├── Approve → Send Email
├── Modify → Generate Reply
└── Timeout → End
```

---

# 📊 Dataset

## Data Sources

| Source | Samples |
|---------|---------|
| Personal Emails | 1,200 |
| Synthetic Emails | 1,600 |

Total:

```
2,800 Emails
```

Distribution:

| Class | Percentage |
|-------|------------|
| Not Spam | 45% |
| Spam | 55% |

---

# 🤖 Models

## Spam Classification Models

The following models were benchmarked:

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- PhoBERT (PEFT)

Final deployed model:

> ✅ PhoBERT PEFT

---

## Large Language Model

Model:

```
Llama-3.3-70B-Versatile
```

Tasks:

- Email understanding
- Need Reply Detection
- Email Summarization
- Draft Reply Generation
- Intent Classification

---

# 🧠 PhoBERT Pipeline

```text
Dataset
    │
    ▼
Preprocessing
    │
    ▼
Train / Validation / Test
    │
    ▼
PhoBERT Fine-tuning
    │
    ▼
Early Stopping
    │
    ▼
Threshold Optimization
    │
    ▼
Final Model
```

---

# 📈 Model Selection Strategy

## Machine Learning

```text
Dataset
   │
Train/Test Split
   │
Optuna
   │
5-Fold Cross Validation
   │
Best Hyperparameters
   │
Refit
   │
Test Evaluation
```

---

## PhoBERT

```text
Dataset
    │
70 / 15 / 15 Split
    │
Train
    │
Validation
    │
Early Stopping
    │
Best Checkpoint
    │
Threshold Optimization
    │
Refit
    │
Test
```

---

# ⚙️ PhoBERT Configuration

| Item | Value |
|------|------|
| Base Model | vinai/phobert-base |
| Hidden Size | 768 |
| Fine-tuning | PEFT |
| Framework | HuggingFace Transformers |
| Optimizer | AdamW |
| Early Stopping | ✓ |
| Threshold Optimization | ✓ |

---

# 📊 Experimental Results

(Add your benchmark table here)

| Model | Accuracy | Precision | Recall | F1 |
|--------|----------|-----------|--------|----|
| Logistic Regression | | | | |
| Decision Tree | | | | |
| Random Forest | | | | |
| XGBoost | | | | |
| PhoBERT | | | | |

---

# 👨‍💻 Human-in-the-Loop

Instead of automatically sending generated replies, the AI Agent first sends:

- Email summary
- Draft reply

to Telegram.

The user can:

- ✅ Approve
- ✏️ Modify
- ❌ Reject

Only approved emails are sent.

---

# 🌐 Deployment

## Spam Classification API

- FastAPI

## Workflow

- LangGraph

## LLM

- Groq API
- Llama-3.3-70B-Versatile

## Model Repository

```
https://huggingface.co/ngcam522/phobertemailspam
```

---

# 🛠️ Tech Stack

- Python
- FastAPI
- HuggingFace Transformers
- PhoBERT
- LangGraph
- Groq API
- Telegram Bot API
- IMAP
- SMTP
- PyTorch

---

# 📌 Future Work

- Attachment Processing
- OCR Support
- RAG Integration
- Multi-class Email Classification
- Long-term Memory
- Multi-language Support

---

# 👤 Author

**Bùi Thị Cẩm Ngoan**

Data Science Student

Ho Chi Minh City Open University

---
