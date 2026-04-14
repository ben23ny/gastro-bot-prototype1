import random


# =========================================
# HERO PROMPTS (BILD / WERBEMOTIV)
# =========================================

def build_hero_prompt(style: str) -> str:
    style = (style or "luxury").lower()

    if style == "luxury":
        return (
            "ultra realistic luxury food photography, premium dessert, "
            "soft cinematic lighting, dark elegant background, "
            "high detail, glossy textures, depth of field, 4k, advertising style"
        )

    if style == "fresh":
        return (
            "fresh vibrant food photography, bright natural lighting, "
            "clean background, colorful dessert, high detail, instagram style"
        )

    if style == "dark":
        return (
            "dark moody food photography, dramatic lighting, "
            "high contrast, cinematic shadows, premium dessert, 4k"
        )

    if style == "minimal":
        return (
            "minimalistic food photography, clean composition, "
            "white background, soft light, high detail"
        )

    # Default
    return (
        "professional food photography, high quality dessert, "
        "soft lighting, realistic, clean composition"
    )


# =========================================
# VIDEO PROMPTS (KI VIDEO GENERATION)
# =========================================

def build_video_prompt(style: str) -> str:
    style = (style or "auto").lower()

    if style == "cinematic_push":
        return (
            "slow cinematic camera push towards dessert, "
            "shallow depth of field, soft light, premium food commercial"
        )

    if style == "soft_float":
        return (
            "smooth floating camera movement around dessert, "
            "light reflections, elegant motion, premium commercial look"
        )

    if style == "dramatic_focus":
        return (
            "dramatic focus pull on dessert, strong lighting contrast, "
            "cinematic shadows, luxury advertisement"
        )

    if style == "luxury_glow":
        return (
            "soft glowing light on dessert, elegant atmosphere, "
            "premium luxury food commercial, slow motion"
        )

    # Default fallback
    return (
        "cinematic food video, smooth motion, soft lighting, "
        "premium advertisement style"
    )


# =========================================
# RANDOM STYLE GENERATOR (WOW EFFEKT)
# =========================================

VIDEO_STYLES = [
    "cinematic_push",
    "soft_float",
    "dramatic_focus",
    "luxury_glow",
]


def get_random_video_style() -> str:
    return random.choice(VIDEO_STYLES)


# =========================================
# STYLE VARIATION SYSTEM (WICHTIG!)
# =========================================

def build_variant_styles(base_style: str, count: int) -> list[str]:
    """
    Erzeugt verschiedene Style-Varianten für A/B Testing
    """
    styles = []

    for i in range(count):
        if i == 0:
            styles.append(base_style)
        else:
            styles.append(random.choice(VIDEO_STYLES))

    return styles