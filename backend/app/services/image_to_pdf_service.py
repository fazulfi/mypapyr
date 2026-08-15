from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import BinaryIO

from PIL import Image, ImageOps

try:
    import img2pdf
except ImportError:
    img2pdf = None

from app.services.paper_policy import PaperStandard

Image.MAX_IMAGE_PIXELS = 20_000_000


@dataclass(frozen=True)
class ImageToPdfRequest:
    images: tuple[bytes | BinaryIO, ...]
    paper: PaperStandard = PaperStandard.A4
    per_image_orientation: bool = True


def _normalise_image(data: bytes | BinaryIO) -> bytes:
    raw = data if isinstance(data, bytes) else data.read()
    with Image.open(BytesIO(raw)) as image:
        image.load()
        oriented = ImageOps.exif_transpose(image).convert("RGB")
        output = BytesIO()
        oriented.save(output, format="JPEG", quality=95)
        return output.getvalue()


def images_to_pdf(req: ImageToPdfRequest, *, timeout: float | None = None) -> bytes:
    if not req.images:
        raise ValueError("at least one image is required")
    normalised = [_normalise_image(item) for item in req.images]
    if img2pdf is None:
        images = [Image.open(BytesIO(item)).convert("RGB") for item in normalised]
        output = BytesIO()
        images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
        return output.getvalue()
    kwargs: dict[str, object] = {}
    kwargs["pagesize"] = (
        img2pdf.papersizes["letter"] if req.paper is PaperStandard.LETTER else img2pdf.papersizes["a4"]
    )
    return img2pdf.convert(normalised, **kwargs)
