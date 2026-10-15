import os 
import io
import time
import base64
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
import fitz
import pandas as pd 
from PIL import Image
from langchain_groq import ChatGroq
from groq import Groq
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

PDF_PATH=""

TEXT_MODEL = "openai/gpt-oss-20b"
VISION_MODEL = "qwen/qwen3.8-27b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

PINECONE_INDEX_NAME = "novacore-multimodal-rag"
PINECONE_NAMESPACE = "fy2026-demo"

IMAGE_DIR = Path("novacore_extracted_images")
IMAGE_DIR.mkdir(exist_ok=True)

print("PDF:", PDF_PATH)
print("Pinecone index:", PINECONE_INDEX_NAME)
print("Pinecone namespace:", PINECONE_NAMESPACE)


text_llm = ChatGroq(
    model=TEXT_MODEL,
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

groq_client=Groq(api_key=os.environ["GROQ_API_KEY"])

# Helper : Convert image to base64 (then after giving this image  base64 url to vision model)

def image_to_data_uri(image_path):
    image_path = Path(image_path)

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail((1600, 1600))

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


## flow chart 
# Image /Chart 
#    |
#  Vision Model
#  Text Summary
#   Embedding 
#   Pinecone
# keep the orginal image path so that final answer can use the real visiual

# Summarize visual 



def summarize_visual(image_path, page_number):
    image_data = image_to_data_uri(image_path)

    prompt = f"""
This visual was extracted from page {page_number} of the NovaCore FY2026 company report.

Describe the useful business information visible in the visual.

If it is a chart or graph:
- mention important values
- mention highest/lowest values
- mention the main trend

If it is a diagram:
- identify important components
- explain the flow or relationships

If it is a normal business image:
- describe the useful factual information

Keep the description concise and factual.
"""

    response = groq_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data},
                    },
                ],
            }
        ],
        temperature=0,
        max_completion_tokens=500,
    )

    return response.choices[0].message.content.strip()



def extract_multimodal_documents(pdf_path):
    pdf = fitz.open(str(pdf_path))

    documents = []
    extracted_xrefs = set()

    for page_index in range(len(pdf)):
        page = pdf[page_index]
        page_number = page_index + 1

        print(f"Processing page {page_number}...")

      
        text = page.get_text("text").strip()

        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "page": page_number,
                        "modality": "text",
                        "source": pdf_path.name,
                    },
                )
            )

        
        # 2. TABLES
       
        try:
            tables = page.find_tables().tables

            for table_number, table in enumerate(tables, start=1):
                df = table.to_pandas()

                if not df.empty:
                    table_text = df.to_markdown(index=False)

                    documents.append(
                        Document(
                            page_content=table_text,
                            metadata={
                                "page": page_number,
                                "modality": "table",
                                "table_number": table_number,
                                "source": pdf_path.name,
                            },
                        )
                    )

        except Exception as error:
            print("Table extraction warning:", error)

       
        # 3. IMAGES / CHARTS / DIAGRAMS
       
        for image_number, image_info in enumerate(
            page.get_images(full=True),
            start=1,
        ):
            xref = image_info[0]

            # Do not process an identical embedded image twice.
            if xref in extracted_xrefs:
                continue

            extracted_xrefs.add(xref)

            image_data = pdf.extract_image(xref)
            image_bytes = image_data["image"]
            image_extension = image_data["ext"]

            image_path = (
                IMAGE_DIR
                / f"page_{page_number}_image_{image_number}.{image_extension}"
            )

            image_path.write_bytes(image_bytes)

            try:
                summary = summarize_visual(
                    image_path=image_path,
                    page_number=page_number,
                )

                documents.append(
                    Document(
                        page_content=summary,
                        metadata={
                            "page": page_number,
                            "modality": "visual",
                            "image_path": str(image_path),
                            "source": pdf_path.name,
                        },
                    )
                )

            except Exception as error:
                print(
                    f"Vision warning on page {page_number}:",
                    error,
                )

    pdf.close()
    return documents


documents = extract_multimodal_documents(PDF_PATH)

print()
print("Total LangChain documents:", len(documents))


# Inspect Extracted Content


rows = []

for doc in documents:
    rows.append(
        {
            "page": doc.metadata["page"],
            "modality": doc.metadata["modality"],
            "preview": doc.page_content[:140].replace("\n", " "),
        }
    )

summary_df = pd.DataFrame(rows)

#display(summary_df)

print("Documents by modality:")
# display(summary_df["modality"].value_counts())


# create embeddings 

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    encode_kwargs={"normalize_embeddings": True},
)

# Detect the exact vector dimension automatically.
EMBEDDING_DIMENSION = len(
    embeddings.embed_query("dimension check")
)

print("Embedding model:", EMBEDDING_MODEL)
print("Embedding dimension:", EMBEDDING_DIMENSION)



pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"]
)

if not pc.has_index(PINECONE_INDEX_NAME):
    print("Creating Pinecone index...")

    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        ),
    )

    # Wait until Pinecone reports that the index is ready.
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        print("Waiting for Pinecone index...")
        time.sleep(2)

    print("Pinecone index created.")
else:
    print("Pinecone index already exists.")

index = pc.Index(PINECONE_INDEX_NAME)

print("Connected to:", PINECONE_INDEX_NAME)
     
