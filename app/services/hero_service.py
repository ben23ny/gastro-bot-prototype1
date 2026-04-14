from app.ai.food_styler import apply_food_style
from app.ai.hero_replicate import build_hero_with_replicate
from app.features.profiles import build_hero_prompt


def generate_hero_image(image_path: str, style_profile: str) -> str:
    styled_path = apply_food_style(image_path)
    prompt = build_hero_prompt(style_profile)
    return build_hero_with_replicate(styled_path, prompt)