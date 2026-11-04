# ⚖️ JurisExtract - Backend API

**JurisExtract** is an AI-powered backend system that reads Indian court judgments (PDFs) and automatically extracts important action items, responsible government departments, and deadlines[cite: 2, 4, 5]. It also supports Human-in-the-Loop verification and regional language translation (Kannada).

---

## 📁 Project File Structure (What Each File Does)

Here is a simple breakdown of all the files in this backend so everyone on the team knows where to look:

* **`main.py` (The Main Server):** Starts the FastAPI web server. It creates all the API endpoints (routes), manages the SQLite database (`juris_extract.db`), saves uploaded PDFs to the `uploads/` folder, and connects all other files together.
* **`document_processor.py` (The PDF Reader):** Reads the uploaded PDF[cite: 2, 5]. First, it tries to extract digital text quickly using `PyMuPDF`[cite: 2]. If the PDF is a scanned image, it automatically switches to `Tesseract OCR` to read the text from images[cite: 2]. Finally, it cuts the long text into smaller 200-word pieces (chunks)[cite: 2, 5].
* **`rag_engine.py` (The Smart Search Engine):** Takes the text chunks and stores them locally in a Vector Database (`ChromaDB`) inside the `vector_db/` folder[cite: 6]. Instead of sending a massive 50-page PDF to the AI, it searches the database using 3 legal queries (orders, timelines, departments) to pull out only the most important paragraphs[cite: 6].
* **`llm_extractor.py` (The AI Brain):** Takes the important paragraphs found by the RAG engine and sends them to Google's Gemini AI. It uses `Pydantic` and `Instructor` to force the AI to reply in a clean, strict JSON format containing the Case Summary, Action Type, Department, Timeline, Confidence Score, and Exact Quotes[cite: 4].
* **`juris_extract.db` (The Database):** A local SQLite database file with two tables: `cases` (stores PDF info and summaries) and `action_items` (stores the extracted tasks and whether a human has verified them)[cite: 3, 5].
* **`requirements.txt` (Dependencies):** Lists the Python libraries needed to run the project[cite: 1].

---

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI, Uvicorn (Python)[cite: 1, 5]
* **Document & OCR Processing:** PyMuPDF (`fitz`), PyTesseract (Google Tesseract OCR), Pillow (PIL)[cite: 1, 2]
* **RAG & Vector Database:** ChromaDB (Local Vector Storage), MiniLM Embeddings (Default Embedding Function)[cite: 1, 6]
* **AI & Structured Extraction:** Google GenAI SDK (`gemini-3.5-flash-lite`), Instructor, Pydantic, Groq[cite: 1, 4]
* **Translation:** Sarvam AI SDK (`sarvam-translate:v1` for English to Kannada translation)[cite: 1, 5]
* **Relational Database:** SQLite3[cite: 3, 5]

---

## 💻 System Requirements

1. **Operating System:** Windows 10/11, macOS, or Linux.
2. **Python:** Version 3.10 or higher.
3. **RAM:** Minimum 4 GB (8 GB recommended for smooth local ChromaDB embedding).
4. **External Software:** 
   * **Tesseract OCR** must be installed on your computer for scanned PDFs[cite: 2]. 
   * *Windows Note:* Install it at `C:\Program Files\Tesseract-OCR\tesseract.exe` (matches line 7 in `document_processor.py`)[cite: 2].
5. **API Keys Required (in `.env` file):**
   * `GEMINI_API_KEY` (From Google AI Studio)[cite: 4]
   * `SARVAM_API_KEY` (From Sarvam AI for translation)

---

## 🔄 Methodology (Step-by-Step Workflow)

Our project follows a **6-step pipeline**:

1. **Document Ingestion & Dual Extraction:** When a user uploads a court judgment PDF, the system checks if it contains selectable digital text[cite: 2, 5]. If not, it converts each page into a high-resolution image (2x zoom) and runs Optical Character Recognition (OCR) to get the text[cite: 2].
2. **Text Chunking:** The extracted text is broken down into 200-word chunks with a 30-word overlap so sentences don't lose their meaning in the middle[cite: 2, 5].
3. **Multi-Query RAG (Retrieval-Augmented Generation):** All chunks are converted into mathematical vectors and saved in ChromaDB[cite: 6]. The system runs 3 automatic searches looking for:
   * *Directives & compliance orders*[cite: 6]
   * *Timelines, deadlines & limitation periods*[cite: 6]
   * *Nodal officers & responsible departments*[cite: 6]
   Duplicate chunks are removed and combined into a concentrated context[cite: 6].
4. **Strict LLM JSON Extraction:** The concentrated context is sent to the LLM with a strict schema. The AI extracts tasks, categorizes them (`Compliance`, `Appeal Consideration`, `Policy Review`, `Other`), assigns a confidence score (0–100), and pulls the exact verbatim quote from the judgment to prevent AI hallucination[cite: 4].
5. **Human-in-the-Loop (HITL) Verification:** All AI outputs are saved in SQLite with the status `pending_review`[cite: 3, 5]. An officer reviews, edits, or approves the items, updating their status to `verified`.
6. **Dashboard & Localization:** Verified tasks are displayed on the Executive Dashboard and can be translated into Kannada (`kn-IN`) using Sarvam AI.

---

## 🏗️ System Architecture

```text
+-------------------------------------------------------------------------+
|                           USER / FRONTEND / SWAGGER                     |
+-------------------------------------------------------------------------+
       | (1. Upload PDF)              | (5. Verify Data)     | (6. Translate)
       v                              v                      v
+-------------------------------------------------------------------------+
|                         FastAPI Server (main.py)                        |
+-------------------------------------------------------------------------+
       |                                                     |
       |---> [document_processor.py]                         |---> [Sarvam AI SDK]
       |     ├─ Digital PDF? -> PyMuPDF (Fast)               |     (English -> Kannada)
       |     └─ Scanned PDF? -> Tesseract OCR (Fallback)     |
       |     └─ Splits into 200-word overlapping chunks      |
       |                                                     |
       |---> [rag_engine.py]                                 |
       |     ├─ Saves vectors locally in ChromaDB            |
       |     └─ Runs 3 Parallel Semantic Searches            |
       |                                                     |
       |---> [llm_extractor.py]                              |
       |     └─ Sends top chunks to Gemini AI + Instructor   |
       |     └─ Returns Strict JSON Action Plan              |
       |                                                     |
       v                                                     |
+------------------------------------------------------------+------------+
|                     SQLite Database (juris_extract.db)                  |
|            [ Table 1: cases ]  <----->  [ Table 2: action_items ]       |
+-------------------------------------------------------------------------+