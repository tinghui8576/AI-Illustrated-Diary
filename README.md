# AI Illustrated Diary 📔✏️

An **AI-powered illustrated diary** that turns daily written memories into visual stories. 
Diary entries are stored as semantic memory using embeddings and a vector database, then converted by an LLM into prompts for **image generation with Stable Diffusion**.

---

## ✨ Features

* 📔 **Diary Entry Input** – Write daily diary entries via a simple interface
* 🧠 **Semantic Memory Storage** – Entries are embedded and stored in **ChromaDB** for long-term memory
* 🔍 **Semantic Search & Retrieval** – Retrieve past diary entries based on semantic similarity
* 🎨 **LLM Prompt Generation** – A LLM converts diary, memories, mood and style into structured prompts
* 🖼️ **Stable Diffusion Image Generation** – Generated prompts are passed directly to a diffusion model
* 🌐 **Streamlit Interface** – Lightweight UI for writing, browsing, and generating images

---

## 🏗️ Project Architecture

```
Diary Project
├── interface.py                # Streamlit UI
├── chroma_store.py             # ChromaDB wrapper & persistence logic
├── Generator/
│   ├── main.py                 # LLM manager and generation logic
│   ├── prompt_generator        # Prompt templates         
│   └── image_generator         # Image generation templates    
├── requirements.txt
├── .gitignore
└── README.md
```
---

## 🚀 Getting Started

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the App

```bash
streamlit run interface.py
```

### 3️⃣ Start Writing

* Browse entries by date
* Add diary entries by choosing mood, style and inputting diary text
* Click generating image, and wait for the generation
* Choose the picture you like, or ask for regeneration if none of them are satisified.

---

## 🧪 Tech Stack

* **LLM**: Llama-3.2 1B Instruct
* **Image Model**: Stable Diffusion v1.5
* **Vector DB**: ChromaDB
* **UI**: Streamlit

---

## 🙌 Author

Created by **Ting-Hui Cheng**

