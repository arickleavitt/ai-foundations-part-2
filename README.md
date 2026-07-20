# Simple Python RAG App

This is a beginner-friendly Retrieval-Augmented Generation app built with:

- Streamlit for the web UI
- ChromaDB for the local vector database
- OpenAI embeddings for indexing documents
- OpenAI chat completions for answering questions

## What Is RAG?

RAG stands for Retrieval-Augmented Generation.

In simple terms:

1. You upload documents.
2. The app splits those documents into smaller chunks.
3. Each chunk is converted into a searchable vector using an embedding model.
4. When you ask a question, the app searches for the most relevant chunks.
5. The AI model answers using those chunks as context.

This helps the model answer questions about your own files instead of relying only on what it already knows.

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
`-- .env.example
```

The app also creates a local `chroma_db` folder after you index documents. That folder stores the vector database.

## Setup

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

Open `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

You can also paste your API key into the app sidebar for the current browser session.
The `.env` file is better for normal local development because you do not need to
paste the key every time you restart the app.

## Run The App

Start Streamlit:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in your terminal.

## Use The App

1. Upload one or more `.txt` or `.md` files.
2. Click **Index uploaded files**.
3. Enter a question about the uploaded documents.
4. Click **Get answer**.
5. Read the answer and expand the source chunks to see what context was used.

## Reset The Local Vector Database

You can reset the database in either of these ways:

- Click **Reset vector database** in the app sidebar.
- Stop the app and delete the `chroma_db` folder manually:

```bash
rm -rf chroma_db
```

The next time you index documents, ChromaDB will recreate the folder.

## Troubleshooting Quota Errors

If you see an error like `insufficient_quota` or `You exceeded your current quota`,
the API key does not currently have usable OpenAI Platform quota. This is different
from the number of tokens available in a prompt or chat context.

Check:

- Your OpenAI Platform billing settings: https://platform.openai.com/settings/organization/billing
- Your API usage page: https://platform.openai.com/usage
- That your API key belongs to the project with available credits: https://platform.openai.com/api-keys

If billing and usage look correct, try creating a new API key for the correct
project and paste that key into the app sidebar.

## Notes

- The embedding model is `text-embedding-3-small`.
- The chat model is `gpt-4.1-mini`.
- ChromaDB stores data locally in `./chroma_db`.
- Uploaded documents are not permanently stored by the app, but their text chunks and embeddings are stored in ChromaDB.
