# 🧬 Medical Research RAG Assistant

## Overview
This project builds an end-to-end **Retrieval-Augmented Generation (RAG)** system that answers medical research questions using **PubMed abstracts** with **source citations**.

It aligns with real production RAG principles — data ingestion, retrieval tuning, prompt grounding, and evaluation.

---

## 🩺 Business Problem
Clinicians cannot keep up with thousands of new papers each year.  
Goal: enable concise, **cited** answers to medical queries using real PubMed data.

---

## Architecture
```
PubMed → Biopython Fetch → CSV
          ↓
Chunking (1000 chars + 200 overlap)
          ↓
OpenAI Embeddings (text-embedding-3-small)
          ↓
FAISS Index (semantic search)
          ↓
Prompted Generation (gpt-4o-mini)
          ↓
Streamlit App + Evaluation Logs
```

---

## Features
✅ Retrieval over 200+ PubMed abstracts  
✅ Grounded, citation-rich responses  
✅ Quality-score confidence metric  
✅ Interactive Streamlit UI  
✅ Automatic evaluation logging  

---

## How to Run Locally
1. **Clone repo & install deps**
   ```bash
   git clone <your-repo-url>
   cd rag-med
   conda create -n rag-med python=3.10 -y
   conda activate rag-med
   pip install -r requirements.txt
   ```

2. **Set API Key**
   ```bash
   echo "OPENAI_API_KEY=REDACTED..." > .env
   ```

3. **Run App**
   ```bash
   streamlit run app.py
   ```

4. **Ask questions**
   - “What are challenges in combating antimicrobial resistance?”
   - “Latest strategies for hypertension control?”

5. **View Logs**
   ```bash
   cat logs/chat_history.csv
   ```

---

## Evaluation
| Metric | Meaning |
|---------|----------|
| Quality Score | Avg cosine similarity of retrieved chunks |
| Response Latency | Time per query |
| Citation Count | Number of distinct sources used |

---

## Tools / Tech Stack
Python · OpenAI API · FAISS · Biopython · Streamlit · Pandas · dotenv  

---

## Limitations & Next Steps
- Currently uses abstracts only; extend to full papers via PubMed Central.  
- Add automated retrieval evaluation (Precision@k).  
- Deploy on FastAPI or Docker for scaling.  

---

## Author
Built by **Tanmay Patel** — Data Scientist passionate about domain-specific RAG systems for Healthcare.
