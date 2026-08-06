from io import BytesIO
from PIL import Image
from app.services.image_to_pdf_service import ImageToPdfRequest, images_to_pdf

def test_images_to_pdf_returns_pdf() -> None:
    output = BytesIO(); Image.new("RGB", (100, 100), "white").save(output, format="JPEG")
    assert images_to_pdf(ImageToPdfRequest((output.getvalue(),)), timeout=1).startswith(b"%PDF")
