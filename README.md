# 🧠 LangGraph Human-in-the-Loop Support System

A minimal **LangGraph-based AI agent** with **MongoDB checkpointing** and **human escalation support**.

> ⚠️ This is a practice project. Can be extended with per-thread auth, queue-based scaling, and proper multi-user support.

---

## 📌 Summary

A **stateful AI support system** where:
- The LLM can **pause execution (interrupt)**
- Escalate to a **human support agent**
- Resume seamlessly with human-provided input

> AI handles most cases → escalates when needed → resumes execution with human input.

---

## 🚀 Features

* 🔁 **Persistent conversations** (MongoDB checkpointing)
* 🧑‍💻 **Human-in-the-loop support escalation**
* 🧰 **Tool-calling LLM (LangChain + LangGraph)**
* 🧵 **Thread-based session management**
* ⚡ **Streaming responses**
* 🛑 Safe handling of interrupted flows

---

## 🏗️ Architecture

```
User → LLM → Tool Call → Interrupt
                          ↓
                 MongoDB (Checkpoint)
                          ↓
                 Support Agent (resume)
                          ↓
                  LLM continues
                          ↓
                      User gets response
```

---

## 📁 Project Structure

```
.
├── app.py        # User-facing chat loop
├── graph.py      # LangGraph definition (LLM + tools)
├── support.py    # Support agent interface (resume flow)
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd <repo>
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Create `.env`

```env
MONGODB_URI=your_mongodb_connection_string
THREAD_ID=8
OPENAI_API_KEY=your_openai_key
```

---

## ▶️ Usage

### 🧑 User Interface

Run:

```bash
python app.py
```

* User can chat normally
* If escalation is needed:

  * System pauses
  * User sees:

```
Your request is being handled by support. Please wait...
```

---

### 🧑‍💻 Support Agent Interface

Run:

```bash
python support.py
```

* Fetches pending interrupt
* Displays prompt like:

```
User has login issue. Provide resolution.
>
```

* Agent inputs solution
* Graph resumes and completes response

---

## 🧠 How It Works

### 1. Tool triggers interrupt

```python
interrupt({
    "query": "User has login issue. Provide resolution."
})
```

This:

* Pauses execution
* Saves state in MongoDB
* Waits for human input

---

### 2. Graph is paused

* Cannot accept new messages
* Only accepts:

```python
Command(resume={"data": ...})
```

---

### 3. Support agent resumes execution

```python
Command(resume={"data": "Reset password using forgot password"})
```

---

### 4. LLM continues

* Tool returns human input
* LLM generates final response
* User gets solution

---

## 🔑 Key Design Decisions

### ❗ Separation of roles

| Component    | Responsibility        |
| ------------ | --------------------- |
| `app.py`     | User interaction only |
| `support.py` | Human support input   |
| `graph.py`   | AI + tool logic       |

---

### ❗ Interrupt handling

* Users **cannot resume execution**
* Only support agents can
* Prevents corrupted state or incorrect flows

---

### ❗ Thread-based state

Each session is identified by:

```python
THREAD_ID
```

This allows:

* Multiple conversations
* Persistent memory
* Resume across processes

---

## ⚠️ Important Notes

* While interrupted:

  * User input is ignored
  * Graph remains paused
* Only `support.py` should resume execution
* No validation is applied to support input (add if needed)

---

## 🧪 Example Flow

```
User: I have a login issue
→ LLM triggers interrupt

User: What's the solution?
→ Ignored (waiting for support)

Support Agent:
→ "Ask user to reset password"

LLM:
→ "Please use the 'Forgot Password' option."
```

---



