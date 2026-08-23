"""Lightweight, dependency-free (Pillow-only) OCR preprocessing.

Deliberately simple per the assessment's own guidance not to over-engineer
this: grayscale + contrast normalization covers the common case (phone-
camera photos and mediocre scans) without pulling in OpenCV for deskewing
or advanced denoising.
"""

from PIL import Image, ImageOps

# Tesseract's accuracy drops noticeably below ~150 DPI-equivalent resolution.
# Upscale small images so tiny scans/photos still OCR reasonably.
MIN_DIMENSION_PX = 1000


def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    grayscale = ImageOps.grayscale(image)
    contrasted = ImageOps.autocontrast(grayscale, cutoff=1)

    width, height = contrasted.size
    smallest_side = min(width, height)
    if smallest_side < MIN_DIMENSION_PX:
        scale = MIN_DIMENSION_PX / smallest_side
        contrasted = contrasted.resize(
            (round(width * scale), round(height * scale)), Image.LANCZOS
        )

    return contrasted
