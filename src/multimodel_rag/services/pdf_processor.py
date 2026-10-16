import hashlib
import fitz
from pathlib import Path
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from multimodel_rag.config import get_settings
from multimodel_rag.services.images import image_to_data_uri
from multimodel_rag.services.llm import get_text_llm,get_vision_llm
from multimodel_rag.services.vector_store import get_embeddings,get_vectorstore



def describe_image(image_path:Path, page_number:int) ->str:
    """Asks the vision model to decribe one image."""

    prompt = (

        f"This image is from page {page_number} of a document. "
        "Describe the important information shown in it. "
        "For charts or graphs, list the key values, labels, and the main trend. "
        "For diagrams, explain the parts and how they connect. "
        "Be concise and factual. Do not add information that is not visible."
    )

    message = HumanMessage(
        content=[
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":image_to_data_uri(image_path)}},
        ]
    )

    return get_vision_llm().invoke([message]).content.strip()



def extract_documents(pdf_path: Path) -> list[Document]:
    """Returns one Document per text block, table, and image description."""
    settings = get_settings()
    image_dir = Path(settings.image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)

    documents: list[Document] = []
    seen_image_ids: set[int] = set()  # the same image can appear on many pages
    source_name = pdf_path.name

    with fitz.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):

            # 1. Plain text
            text = page.get_text().strip()
            if text:
                documents.append(Document(
                    page_content=text,
                    metadata={"source": source_name, "page": page_number, "type": "text"},
                ))

            # 2. Tables, stored as Markdown (easy for the LLM to read)
            for table in page.find_tables().tables:
                table_df = table.to_pandas()
                if not table_df.empty:
                    documents.append(Document(
                        page_content=table_df.to_markdown(index=False),
                        metadata={"source": source_name, "page": page_number, "type": "table"},
                    ))

            # 3. Images, charts, and diagrams
            for image_number, image_info in enumerate(page.get_images(full=True), start=1):
                image_id = image_info[0]
                if image_id in seen_image_ids:
                    continue
                seen_image_ids.add(image_id)

                image = pdf.extract_image(image_id)
                image_path = image_dir / (
                    f"{pdf_path.stem}_p{page_number}_img{image_number}.{image['ext']}"
                )
                image_path.write_bytes(image["image"])

                try:
                    description = describe_image(image_path, page_number)
                except Exception:
                    continue  # skip this image, keep processing the PDF

                documents.append(Document(
                    page_content=description,
                    metadata={
                        "source": source_name,
                        "page": page_number,
                        "type": "visual",
                        "image_path": str(image_path),
                    },
                ))

    return documents


def make_chunk_id(doc: Document) -> str:
    """Same content always gives the same ID, so duplicates are overwritten, not added."""
    raw = (
        f"{doc.metadata['source']}|{doc.metadata['page']}|"
        f"{doc.metadata['type']}|{doc.page_content}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def ingest_pdf(pdf_path: Path) -> int:
    """Saves a PDF's content to Pinecone. Returns how many chunks were stored."""
    documents = extract_documents(pdf_path)
    if not documents:
        return 0

    chunk_ids = [make_chunk_id(doc) for doc in documents]
    get_vectorstore().add_documents(documents, ids=chunk_ids)
    return len(documents)