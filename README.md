#  AI Agent for Vietnamese Email Management

An intelligent AI Agent for Vietnamese email management that combines **Machine Learning** for classify emails as Spam or Not Spam , **PhoBERT**, **Large Language Models (LLMs)** and **LangGraph** to automatically classify spam, summarize emails, generate replies, and assist users through a Human-in-the-Loop workflow.

---

#  Features

- Read unread emails from Gmail
- Classify emails as Spam or Not Spam using with Word Segmentation and TF-IDF Features
- Analyze email content with Llama-3.3-70B
- Generate concise email summaries
- Draft context-aware email replies
- Orchestrate the workflow with LangGraph
- Support Human-in-the-Loop approval via Telegram
- Automatically send approved replie

---

# System Architecture

<p align="center">
<img <img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/320d3a7a-7b8a-4b6a-a7ef-6fb51c5f1363" />

</p>

The system consists of four major components:

| Component | Description |
|------------|-------------|
| Spam Classification | PhoBERT-based email classification |
| LLM | Email understanding, summarization and reply generation |
| LangGraph | Workflow orchestration |
| Telegram Bot | Human approval before sending email |

---

#  AI Agent Workflow

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

#  LangGraph Design

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

#  Dataset

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

#  Models

## Spam Classification Models

The following models were benchmarked:

- Logistic Regression
- Random Forest
- XGBoost
- PhoBERT (PEFT)

Final deployed model:

> Logistic Regression 
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

#  PhoBERT Pipeline

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

#  Model Selection Strategy

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

## PhoBERT with Parameter-Efficient Fine-Tuning (PEFT)

A lightweight fine-tuning strategy was adopted by freezing the entire PhoBERT encoder and training only a custom classifier head.

| Configuration | Value |
|--------------|-------|
| Base Model | `vinai/phobert-base` |
| Fine-tuning Strategy | PEFT |
| Trainable Parameters | ~592K |
| Reduction | ~227× fewer trainable parameters |
| Benefit | Lower memory usage and faster training |

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

#  PhoBERT Configuration

| Item | Value |
|-------|-------|
| Base Model | `vinai/phobert-base` |
| Hidden Size | 768 |
| Fine-Tuning Strategy | PEFT |
| Framework | HuggingFace Transformers |
| Optimizer | AdamW |
| Learning Rate | 1e-4 |
| Dropout Rate | 0.2 |
| Early Stopping | ✓ |
| Threshold Optimization | 0.9 |


---

#  Experimental Results

## 1. Performance with the Default Decision Threshold

All classification models were initially evaluated on the independent test set using the default decision threshold of 0.5 before threshold optimization was performed. 

<p align="center">
 <img src="https://github.com/user-attachments/assets/71ba533d-5bf0-467b-8dee-eb75e8643ee5" width="700">
</p>

<p align="center"><i>Figure 1. Classification performance on the test set with the default threshold (0.5).</i></p>

---
### Comments

- PhoBERT achieved lower performance, likely due to the relatively small training dataset (~2,000 training samples), which may not be sufficient for a deep learning model to learn and optimize robust contextual representations effectively.
- In contrast, traditional machine learning models combined with TF-IDF features demonstrated superior performance on this small-to-medium-sized dataset.

### Selected Model for Deployment

**Logistic Regression** was selected as the final deployment model. Although **Random Forest** achieved slightly higher Precision, Logistic Regression was preferred because it obtained the highest **Recall for the Not Spam class (94.15%)**. This is particularly important for the business objective, as it minimizes the risk of incorrectly classifying legitimate emails as spam, thereby reducing the number of critical emails that may be missed.


### Key Findings

- **Logistic Regression** achieved the best overall performance among all evaluated models.
- Optimizing the decision threshold from **0.5** to **0.9** improved the balance between Precision and Recall for the target business objective.
- After selecting the optimal architecture and decision threshold, the model was **retrained (refit) using the entire dataset** to maximize the amount of training data before deployment.
- The refitted model was then deployed to **Hugging Face Hub** and integrated into the AI Agent email management workflow for production inference.



#  Human-in-the-Loop

Instead of automatically sending generated replies, the AI Agent first sends:

- Email summary
- Draft reply

to Telegram.

The user can:

- Approve
-  Modify
-  Reject

Only approved emails are sent.

---

#  Deployment

## Spam Classification API

- FastAPI

## Workflow

- LangGraph

## LLM

- Groq API
- Llama-3.3-70B-Versatile

## Model Repository

```
https://huggingface.co/ngcam522/email-spam-tfidf
```

---
#  User Interface

The AI Agent provides a simple web interface built with **Streamlit**, allowing users to configure email credentials, Telegram settings, and interact with the workflow in real time.

Main features:

- Configure Gmail credentials
- Configure Telegram Bot settings
- Start the AI Agent
- View email summaries
- Review AI-generated replies
- Monitor the workflow execution

<p align="center">
<img width="2048" height="956" alt="image" src="https://github.com/user-attachments/assets/a5dca1a2-c33d-4135-875d-edce9dc13fa4" />

</p>

---
#  Installation

Clone the repository

```bash
git clone https://github.com/your-username/your-repository.git

cd your-repository
```

Create a virtual environment (optional)

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install the required packages

```bash
pip install -r requirements.txt
```

---
#  Usage

Launch the Streamlit application

```bash
streamlit run app.py
```

After opening the web interface, provide the following configuration:

| Setting | Description |
|----------|-------------|
| Gmail Address | Your Gmail account |
| Gmail App Password | Gmail App Password (16 characters) |
| Telegram Bot Token | Bot token created with BotFather |
| Telegram Chat ID | Your Telegram chat ID |

Once the configuration is completed:

1. Connect to your Gmail account.
2. The AI Agent continuously monitors unread emails.
3. PhoBERT classifies each email as **Spam** or **Not Spam**.
4. If the email is **Not Spam**, the LLM analyzes its content.
5. The LLM generates:
   - Email summary
   - Reply recommendation
   - Draft reply
6. The summary and draft reply are sent to Telegram.
7. The user can:
   - Approve
   - Modify
   - Reject
8. If approved, the email is automatically sent through Gmail.

---


#  Tech Stack

- Python
- FastAPI
- Streamlit
- HuggingFace Transformers
- PhoBERT
- LangGraph
- Groq API
- Telegram Bot API
- IMAP
- SMTP
- PyTorch

---

#  Future Work

- Attachment Processing
- OCR Support
- RAG Integration
- Multi-class Email Classification
- Long-term Memory
- Multi-language Support

---

#  Author

**Bùi Thị Cẩm Ngoan**

Data Science Student

Ho Chi Minh City Open University

---
