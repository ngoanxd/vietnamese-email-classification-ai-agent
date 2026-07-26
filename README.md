# 🛡️ AI Agent for Vietnamese Email Management

An intelligent AI Agent for Vietnamese email management that combines **Machine Learning**, **PhoBERT**, **Large Language Models (LLMs)** and **LangGraph** to automatically classify spam, summarize emails, generate replies, and assist users through a Human-in-the-Loop workflow.

---

# ✨ Features

- Read unread emails from Gmail
- Classify emails as Spam or Not Spam using PhoBERT
- Analyze email content with Llama-3.3-70B
- Generate concise email summaries
- Draft context-aware email replies
- Orchestrate the workflow with LangGraph
- Support Human-in-the-Loop approval via Telegram
- Automatically send approved replie

---

# 🏗️ System Architecture

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

# ⚙️ PhoBERT Configuration

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

# 📊 Experimental Results

## 1. Performance with the Default Decision Threshold

The PhoBERT-PEFT model was first evaluated on the independent test set using the default decision threshold of **0.5**.

<p align="center">
  <img src="https://github.com/user-attachments/assets/ed15a8bc-dfcb-467f-9914-e767335c25a1" width="700">
</p>

<p align="center"><i>Figure 1. Classification performance on the test set with the default threshold (0.5).</i></p>

---

## 2. Decision Threshold Optimization

To better satisfy the business objective, the decision threshold was optimized using the **validation set**. Different threshold values were evaluated, and **0.9** was selected as the optimal threshold because it achieved the best trade-off between Precision and Recall.

<p align="center">
  <img src="https://github.com/user-attachments/assets/a4fdca73-e9f5-407c-afad-a6140acbbc8d" width="450">
</p>

<p align="center"><i>Figure 2. Threshold selection based on validation performance.</i></p>

---

## 3. Final Evaluation

After selecting the optimal threshold (**0.9**), the final PhoBERT-PEFT model was evaluated on the independent test set.

<p align="center">
  <img src="https://github.com/user-attachments/assets/928d6efc-8bd3-406c-9051-606d5ab07c29" width="450">
</p>

<p align="center"><i>Figure 3. Final performance of the PhoBERT-PEFT model on the test set using the optimized decision threshold.</i></p>

---

### Key Findings

- PhoBERT-PEFT achieved the best overall performance among all evaluated models.
- Optimizing the decision threshold from **0.5** to **0.9** improved the balance between Precision and Recall for the target business objective.
- The final model was selected for deployment and integrated into the AI Agent email management workflow.



# 👨‍💻 Human-in-the-Loop

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
