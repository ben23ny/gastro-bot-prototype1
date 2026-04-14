from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ProgressState:
    status: str
    step: str
    progress: int
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CaptionResult:
    instagram_caption: str
    hashtags: str
    story_text: str
    promo_text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VariantResult:
    label: str
    style_profile: str
    video_mode: str
    video_style: str
    hero_image: str
    video: str
    hero_width: int
    hero_height: int
    caption: CaptionResult

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["caption"] = self.caption.to_dict()
        return data


@dataclass
class GenerationResult:
    original_image: str
    original_width: int
    original_height: int
    headline: str
    subline: str
    variant_count: int
    variants: list[VariantResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_image": self.original_image,
            "original_width": self.original_width,
            "original_height": self.original_height,
            "headline": self.headline,
            "subline": self.subline,
            "variant_count": self.variant_count,
            "variants": [variant.to_dict() for variant in self.variants],
        }