
import os
import re
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from document_reader import read_all_pdfs

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

llm = LLM(
    model="gemini/gemini-3.8-flash",
    api_key=api_key,
)

document_agent = Agent(
    role="Document Question Answering Assistant",
    goal="Answer questions using relevant evidence from the supplied document.",
    backstory=(
        "You carefully analyze document excerpts. "
        "You answer only when supported by the provided text. "
        "If evidence is insufficient, say so clearly."
    ),
    llm=llm,
    verbose=False,
)


def split_into_chunks(text, chunk_size=2500, overlap=400):
    """Split text into overlapping chunks."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - overlap

    return chunks


def retrieve_relevant_chunks(document_text, question, top_k=5):
    """Rank document chunks by keyword overlap with the question."""
    chunks = split_into_chunks(document_text)

    if not chunks:
        return ""

    stop_words = {
        "the", "is", "are", "was", "were", "what", "when",
        "where", "who", "why", "how", "does", "did", "do",
        "and", "or", "of", "to", "in", "for", "on", "a",
        "an", "with", "from", "by", "about", "explain",
        "describe", "tell", "me", "please"
    }

    question_words = set(
        re.findall(r"[a-zA-Z0-9]+", question.lower())
    ) - stop_words

    scored_chunks = []

    for index, chunk in enumerate(chunks):
        chunk_words = set(
            re.findall(r"[a-zA-Z0-9]+", chunk.lower())
        )
        score = len(question_words & chunk_words)
        scored_chunks.append((score, index, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    selected = [
        item for item in scored_chunks[:top_k]
        if item[0] > 0
    ]

    if not selected:
        # Fallback: provide initial chunks rather than no context.
        selected = scored_chunks[:2]

    # Restore original document order for readability.
    selected.sort(key=lambda item: item[1])

    return "\n\n".join(
        f"Document excerpt {index + 1}:\n{chunk}"
        for _, index, chunk in selected
    )


def answer_question(document_text, question):
    relevant_text = retrieve_relevant_chunks(
        document_text,
        question,
        top_k=5,
    )

    if not relevant_text.strip():
        return "No readable text was found in this document."

    task = Task(
        description=(
            "Answer the user's question using the supplied excerpts. "
            "The excerpts may come from different parts of the document.\n\n"
            f"DOCUMENT EXCERPTS:\n{relevant_text}\n\n"
            f"QUESTION:\n{question}\n\n"
            "Give a clear answer based on the evidence. "
            "If the excerpts do not contain the answer, state that "
            "the relevant information was not found in the retrieved "
            "excerpts. Do not invent facts."
        ),
        expected_output="A clear, evidence-based answer to the question.",
        agent=document_agent,
    )

    crew = Crew(
        agents=[document_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    return str(crew.kickoff())


if __name__ == "__main__":
    documents = read_all_pdfs()

    if not documents:
        print("No PDFs found in the documents folder.")
        raise SystemExit(1)

    print("Available documents:")
    for filename in documents:
        print(f"- {filename}")

    selected_document = next(iter(documents))
    document_text = documents[selected_document]

    if document_text.startswith("Error:") or not document_text.strip():
        print(f"Could not read {selected_document}.")
        raise SystemExit(1)

    print(f"\nUsing document: {selected_document}")
    print("Enter 'exit' to quit.")

    while True:
        question = input("\nAsk a question about the PDF: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            print("\nAnswer:")
            print(answer_question(document_text, question))
        except Exception as error:
            print(f"\nError: {error}")
