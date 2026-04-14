from app.features.branding import normalize_style_profile


HERO_PROMPTS = {
    "luxury": (
        "Transform this restaurant snapshot into a premium luxury dessert advertisement. "
        "Keep the exact dessert recognizable. Use elegant studio lighting, dark refined background, "
        "high-end food photography, premium editorial feel, realistic product details, "
        "natural but appetizing colors, no cartoon look, no surreal changes."
    ),
    "social": (
        "Transform this product photo into a bold modern Instagram dessert advertisement. "
        "Keep the exact dessert recognizable. Create an eye-catching premium social media look, "
        "clean dramatic background, vibrant appetizing colors, realistic food-commercial quality."
    ),
    "fresh": (
        "Transform this dessert photo into a bright fresh premium food advertisement. "
        "Keep the exact product recognizable. Use soft clean light, appetizing freshness, "
        "elegant modern background, realistic food photography."
    ),
    "dark": (
        "Transform this dessert photo into a dark dramatic premium advertisement. "
        "Keep the exact product recognizable. Use moody cinematic lighting, strong contrast, "
        "elegant dark background, luxury premium food styling."
    ),
}

VIDEO_PROMPTS = {
    "cinematic_push": (
        "Create a premium dessert advertisement video from this hero image. "
        "Use a slow cinematic push-in camera move, subtle realism, elegant product focus, "
        "no morphing, no deformation, realistic premium food commercial feel."
    ),
    "soft_float": (
        "Create a premium dessert ad video from this hero image with gentle floating camera motion, "
        "soft elegant movement, natural premium realism, no object deformation, no surreal motion."
    ),
    "dramatic_focus": (
        "Create a dramatic premium dessert ad video from this hero image with moody focus transitions, "
        "subtle cinematic movement, elegant premium lighting, realistic motion only, no morphing."
    ),
    "luxury_glow": (
        "Create a luxury dessert commercial video from this hero image with subtle glow highlights, "
        "gentle premium camera movement, refined commercial realism, no floating objects, no distortion."
    ),
}


def build_hero_prompt(style_profile: str) -> str:
    style = normalize_style_profile(style_profile)
    return HERO_PROMPTS[style]


def build_video_prompt(video_style: str) -> str:
    return VIDEO_PROMPTS.get(video_style, VIDEO_PROMPTS["cinematic_push"])