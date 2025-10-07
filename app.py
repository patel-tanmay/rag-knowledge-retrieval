# --- app.py : Streamlit Medical RAG Assistant --------------------------------
import os
import json
import time
import numpy as np
import pandas as pd
import faiss
from openai import OpenAI
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# --- Config & Setup ---
load_dotenv()  # loads .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_EMBED = "text-embedding-3-small"
MODEL_CHAT = "gpt-4o-mini"

index = faiss.read_index("indexes/pubmed.index")
with open("indexes/corpus.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/chat_history.csv"


# --- Helper functions ---
def retrieve_top_k(question: str, k: int = 3):
    q_vec = client.embeddings.create(model=MODEL_EMBED, input=[question]).data[0].embedding
    q_vec = np.array(q_vec, dtype="float32")
    q_vec /= np.linalg.norm(q_vec)
    scores, idxs = index.search(q_vec.reshape(1, -1), k)
    results = []
    for score, idx in zip(scores[0], idxs[0]):
        results.append({
            "score": float(score),
            "title": corpus[idx]["title"],
            "text": corpus[idx]["text"],
            "url": corpus[idx]["url"]
        })
    return results


def build_prompt(question: str, contexts: list[dict]):
    context_texts = []
    for i, ctx in enumerate(contexts, start=1):
        context_texts.append(f"[Source {i}] {ctx['text']}\n(Citation: {ctx['url']})")
    joined = "\n\n".join(context_texts)
    prompt = f"""
You are a medical research assistant.
Use ONLY the retrieved context below to answer the question.
If the answer cannot be found, say "Not enough information in the retrieved papers."

Question: {question}

Retrieved Context:
{joined}

Instructions:
1. Answer concisely and factually.
2. Cite sources by [Source #].
3. Do not include information not in the context.
"""
    return prompt.strip()


def generate_answer(question: str, k: int = 3):
    hits = retrieve_top_k(question, k=k)
    prompt = build_prompt(question, hits)
    response = client.chat.completions.create(
        model=MODEL_CHAT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    answer = response.choices[0].message.content
    quality = round(np.mean([h["score"] for h in hits]), 3)
    citations = [
        {"title": h["title"], "url": h["url"], "score": round(h["score"], 3)}
        for h in hits
    ]
    return answer, quality, citations


def log_interaction(question, answer, quality, citations):
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer,
        "quality": quality,
        "citations": json.dumps(citations),
    }
    df = pd.DataFrame([row])
    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(LOG_FILE, index=False)


# --- Streamlit UI ---
st.set_page_config(page_title="Medical RAG Assistant", page_icon="🧬", layout="wide")

st.title("Medical Research RAG Assistant")
st.markdown(
    "Ask questions about medical research papers — answers are grounded in retrieved PubMed abstracts with full citations."
)

question = st.text_input("Enter your medical question:")

if st.button("Generate Answer"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving and generating answer..."):
            start = time.time()
            answer, quality, citations = generate_answer(question)
            end = time.time()

        st.markdown("### Answer")
        st.write(answer)

        st.markdown(f"**Quality Score:** {quality:.3f}  |  ⏱️ Time: {end - start:.1f}s")

        st.markdown("### 📚 Sources")
        for i, c in enumerate(citations, start=1):
            st.markdown(
                f"[**Source {i}**]({c['url']})  \n"
                f"{c['title']}  \n"
                f"_Relevance: {c['score']:.2f}_"
            )

        log_interaction(question, answer, quality, citations)
        st.success("Logged to chat_history.csv")

st.markdown("---")
st.caption("Built with OpenAI + FAISS + Streamlit · © 2025")
