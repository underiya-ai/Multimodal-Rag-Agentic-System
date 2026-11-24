import io
from pathlib import Path
from PIL import Image
from langchain_core.documents import Document

from multimodel_rag.logger import logger, setup_logger
from multimodel_rag.services.images import image_to_data_uri
from multimodel_rag.services.llm import get_text_llm, get_vision_llm
from multimodel_rag.services.pdf_processor import make_chunk_id


def test_llm_initialization():
    text_llm = get_text_llm()
    vision_llm = get_vision_llm()

    assert text_llm is not None
    assert vision_llm is not None
    # Vision LLM must use the groq api key
    assert vision_llm.groq_api_key is not None


def test_image_to_data_uri(tmp_path):
    img_file = tmp_path / "sample.png"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(img_file)

    data_uri = image_to_data_uri(img_file)
    assert data_uri.startswith("data:image/jpeg;base64,")


def test_make_chunk_id():
    doc1 = Document(page_content="Same content", metadata={"source": "test.pdf", "page": 1, "type": "text"})
    doc2 = Document(page_content="Same content", metadata={"source": "test.pdf", "page": 1, "type": "text"})
    doc3 = Document(page_content="Different", metadata={"source": "test.pdf", "page": 1, "type": "text"})

    id1 = make_chunk_id(doc1)
    id2 = make_chunk_id(doc2)
    id3 = make_chunk_id(doc3)

    assert id1 == id2
    assert id1 != id3


def test_logger():
    custom_logger = setup_logger("test_logger")
    assert custom_logger.name == "test_logger"
    assert logger is not None
