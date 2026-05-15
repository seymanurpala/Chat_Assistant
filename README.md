# Chatbot Project

This project is a modern AI chatbot application built with Flask.  
Users can create conversations, view chat history, and interact with an LLM model powered by the Groq API.

---
## Screenshot

![Chatbot UI](images/chatbot.png)

## Features

- Modern chatbot interface
- Conversation history system
- Create new conversations
- Delete conversations
- Store chat history in a JSON file
- Flask backend architecture
- Groq API integration
- AI assistant with natural responses

---

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Groq API
- dotenv

---

## Project Structure

```bash
chatbot/
│
├── app.py
├── chatbot.py
├── routes.py
├── chat_history.json
├── .env
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
```

---

## Installation

### 1. Clone the project

```bash
git clone <repo-link>
cd chatbot
```

### 2. Install required packages

```bash
pip install flask groq python-dotenv httpx
```

### 3. Create a `.env` file

```env
GROQ_API_KEY=your_api_key
```

---

## Run the Project

```bash
python app.py
```

After starting the application, open:

```bash
http://127.0.0.1:5000
```

---

## Model Used

The following LLM model is used in this project:

```python
llama-3.3-70b-versatile
```

---

## System Prompt

The chatbot is designed to:

- Respond naturally
- Give short and understandable answers
- Avoid giving misleading information
- Provide practical solutions when possible

---

## API Endpoints

### Get Conversations

```http
GET /api/conversations
```

### Create Conversation

```http
POST /api/conversations
```

### Get Conversation

```http
GET /api/conversations/<conversation_id>
```

### Delete Conversation

```http
DELETE /api/conversations/<conversation_id>
```

### Send Message

```http
POST /api/chat
```

---

## Interface Features

- Conversation history on the left sidebar
- Chat area on the right side
- Responsive design
- Clean and modern UI

---

## Purpose

This project was developed to understand the working principles of Large Language Models (LLMs) and transformer-based chatbot systems.  
It also aims to provide practical experience with Flask backend development and API integration.