import hashlib
import os
from pathlib import Path

import chromadb
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


# Load environment variables from a local .env file.
# override=True lets Streamlit pick up a changed .env file after reruns.
load_dotenv(override=True)


# Basic app settings.
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "uploaded_documents"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4.1-mini"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4
ENV_PATH = Path(".env").resolve()


def get_openai_client(api_key):
    """Create an OpenAI client when an API key is available."""
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def describe_api_key(api_key):
    """Return a safe, partial label for the active API key."""
    if len(api_key) <= 8:
        return "short key"
    return f"ending in ...{api_key[-6:]}"


def get_chroma_collection():
    """Open the local persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def split_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split long text into overlapping chunks for better retrieval."""
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    chunks = []
    start = 0

    while start < len(cleaned_text):
        end = start + chunk_size
        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def make_chunk_id(filename, chunk_index, chunk_text):
    """Create a stable unique ID for each uploaded chunk."""
    digest = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()[:16]
    return f"{filename}-{chunk_index}-{digest}"


def embed_texts(client, texts):
    """Send text to OpenAI and return embedding vectors."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def show_openai_error(error, action):
    """Show beginner-friendly messages for common OpenAI API errors."""
    error_text = str(error)

    if "insufficient_quota" in error_text:
        st.error(
            f"{action} failed because this API key does not have usable OpenAI "
            "Platform quota."
        )
        st.info(
            "This is separate from how many tokens fit in a prompt. Check the "
            "OpenAI Platform billing page, project limits, and whether the API "
            "key belongs to the project with available credits. If you have more "
            "than one project, switch projects in the OpenAI dashboard and create "
            "a key from the project that has billing enabled."
        )
        st.markdown(
            "- Billing: https://platform.openai.com/settings/organization/billing\n"
            "- Usage: https://platform.openai.com/usage\n"
            "- API keys: https://platform.openai.com/api-keys"
        )
    elif "rate_limit" in error_text or "429" in error_text:
        st.error(f"{action} failed because the OpenAI API rate limit was reached.")
        st.info("Wait a minute and try again, or index fewer/smaller files at once.")
    else:
        st.error(f"{action} failed: {error}")


def index_uploaded_files(openai_client, collection, uploaded_files):
    """Read uploaded files, split them, embed them, and store them in ChromaDB."""
    all_chunks = []
    all_ids = []
    all_metadata = []

    for uploaded_file in uploaded_files:
        text = uploaded_file.getvalue().decode("utf-8", errors="replace")
        chunks = split_text(text)

        for index, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(make_chunk_id(uploaded_file.name, index, chunk))
            all_metadata.append(
                {
                    "source": uploaded_file.name,
                    "chunk_index": index,
                    "total_chunks": len(chunks),
                }
            )

    if not all_chunks:
        return 0

    # Batch embeddings keep the code simple and reduce API calls.
    embeddings = embed_texts(openai_client, all_chunks)

    # Upsert replaces existing chunks with the same ID instead of duplicating them.
    collection.upsert(
        ids=all_ids,
        documents=all_chunks,
        metadatas=all_metadata,
        embeddings=embeddings,
    )

    return len(all_chunks)


def retrieve_relevant_chunks(openai_client, collection, question, top_k=TOP_K):
    """Embed the question and retrieve the most relevant chunks from ChromaDB."""
    question_embedding = embed_texts(openai_client, [question])[0]
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        chunks.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return chunks


def answer_question(openai_client, question, chunks):
    """Ask the chat model to answer using only the retrieved context."""
    context = "\n\n".join(
        f"Source: {chunk['metadata']['source']} "
        f"(chunk {chunk['metadata']['chunk_index'] + 1})\n{chunk['text']}"
        for chunk in chunks
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant answering questions with retrieved "
                "document context. If the answer is not in the context, say you "
                "do not know based on the uploaded documents."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        },
    ]

    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content


def reset_chroma_collection():
    """Delete the app collection while keeping the local ChromaDB directory."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection_names = [
        collection.name if hasattr(collection, "name") else collection
        for collection in client.list_collections()
    ]
    if COLLECTION_NAME in collection_names:
        client.delete_collection(name=COLLECTION_NAME)


def test_openai_key(openai_client):
    """Make a tiny embedding request to verify that the key has API quota."""
    embed_texts(openai_client, ["test"])


st.set_page_config(page_title="Simple RAG App")
st.title("Simple RAG App")
st.write("Upload text or Markdown files, index them locally, and ask questions.")


collection = get_chroma_collection()


with st.sidebar:
    st.header("OpenAI API key")
    env_api_key = os.getenv("OPENAI_API_KEY", "")
    st.caption(f".env path: {ENV_PATH}")
    if env_api_key.strip():
        st.caption(f".env OPENAI_API_KEY found ({describe_api_key(env_api_key)}).")
    else:
        st.caption(".env OPENAI_API_KEY not found.")

    entered_api_key = st.text_input(
        "API key",
        value="",
        type="password",
        placeholder="sk-...",
        help="Leave blank to use OPENAI_API_KEY from your .env file.",
    )
    key_source = "sidebar" if entered_api_key.strip() else ".env"
    api_key = entered_api_key.strip() or env_api_key.strip()

    if api_key:
        st.success(f"API key loaded from {key_source} ({describe_api_key(api_key)}).")
    else:
        st.warning("Add OPENAI_API_KEY to .env or paste a key here.")
        st.code("OPENAI_API_KEY=your_api_key_here", language="bash")

    openai_client = get_openai_client(api_key)

    if openai_client and st.button("Test API key"):
        with st.spinner("Testing API key..."):
            try:
                test_openai_key(openai_client)
            except OpenAIError as exc:
                show_openai_error(exc, "API key test")
            except Exception as exc:
                st.error(f"API key test failed: {exc}")
            else:
                st.success("API key works for OpenAI embeddings.")

    st.header("Local database")
    st.write(f"Storage folder: `{Path(CHROMA_PATH).resolve()}`")
    st.write(f"Indexed chunks: `{collection.count()}`")

    if st.button("Reset vector database"):
        reset_chroma_collection()
        st.success("Vector database reset. Refresh the page to see the new count.")


st.header("1. Upload documents")
uploaded_files = st.file_uploader(
    "Choose .txt or .md files",
    type=["txt", "md"],
    accept_multiple_files=True,
)

if st.button("Index uploaded files"):
    if openai_client is None:
        st.warning("Add your OpenAI API key before indexing documents.")
    elif not uploaded_files:
        st.warning("Upload at least one .txt or .md file before indexing.")
    else:
        with st.spinner("Indexing documents..."):
            try:
                indexed_count = index_uploaded_files(
                    openai_client, collection, uploaded_files
                )
            except OpenAIError as exc:
                show_openai_error(exc, "Indexing")
            except Exception as exc:
                st.error(f"Indexing failed: {exc}")
            else:
                if indexed_count == 0:
                    st.warning("The uploaded files did not contain any readable text.")
                else:
                    st.success(f"Indexed {indexed_count} chunks.")


st.header("2. Ask a question")
question = st.text_input("Question about your uploaded documents")

if st.button("Get answer"):
    if openai_client is None:
        st.warning("Add your OpenAI API key before asking a question.")
    elif not question.strip():
        st.warning("Enter a question before asking.")
    elif collection.count() == 0:
        st.warning("Index at least one document before asking a question.")
    else:
        with st.spinner("Retrieving context and generating an answer..."):
            try:
                source_chunks = retrieve_relevant_chunks(
                    openai_client, collection, question.strip()
                )
                answer = answer_question(openai_client, question.strip(), source_chunks)
            except OpenAIError as exc:
                show_openai_error(exc, "Question answering")
            except Exception as exc:
                st.error(f"Question answering failed: {exc}")
            else:
                st.subheader("Answer")
                st.write(answer)

                st.subheader("Source chunks used")
                for index, chunk in enumerate(source_chunks, start=1):
                    metadata = chunk["metadata"]
                    with st.expander(
                        f"{index}. {metadata['source']} - "
                        f"chunk {metadata['chunk_index'] + 1} "
                        f"(distance: {chunk['distance']:.3f})"
                    ):
                        st.write(chunk["text"])
