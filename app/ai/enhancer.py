import shutil
from pathlib import Path


def enhance_image(image_path: str) -> str:
    """
    Dummy Image Enhancer.
    Hier kann später eine echte AI integriert werden.
    """

    source = Path(image_path)

    enhanced_path = source.parent / f"enhanced_{source.name}"

    shutil.copy(source, enhanced_path)

    return str(enhanced_path)