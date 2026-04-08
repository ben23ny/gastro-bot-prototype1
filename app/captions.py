from dataclasses import dataclass


@dataclass
class CaptionBundle:
    instagram_caption: str
    hashtags: str
    story_text: str
    promo_text: str


STYLE_HASHTAGS = {
    "luxury": [
        "#dessertliebe",
        "#premiumdessert",
        "#eisgenuss",
        "#foodmarketing",
        "#gastrocontent",
        "#desserttime",
        "#süßergenuss",
        "#luxuryfood",
    ],
    "social": [
        "#instafood",
        "#foodreel",
        "#dessertlover",
        "#eisliebe",
        "#foodcontent",
        "#reelready",
        "#sweettooth",
        "#foodie",
    ],
    "fresh": [
        "#frischgenießen",
        "#dessertmoment",
        "#fruchtig",
        "#sommergefühle",
        "#eisdessert",
        "#freshfood",
        "#genussmoment",
        "#leckerschmecker",
    ],
    "dark": [
        "#premiumtaste",
        "#dessertart",
        "#darkmoodfood",
        "#genusspur",
        "#foodaesthetic",
        "#dessertinspiration",
        "#feinschmecker",
        "#specialdessert",
    ],
}


def _normalize(style_profile: str) -> str:
    value = (style_profile or "luxury").strip().lower()
    return value if value in STYLE_HASHTAGS else "luxury"


def build_caption_bundle(
    headline: str,
    subline: str,
    style_profile: str,
) -> CaptionBundle:
    style = _normalize(style_profile)
    hashtags = " ".join(STYLE_HASHTAGS[style])

    instagram_caption = (
        f"{headline}\n\n"
        f"{subline}\n\n"
        "Mit Liebe zum Detail serviert und perfekt für den nächsten Genussmoment. "
        "Jetzt entdecken, genießen und direkt Lust auf mehr bekommen."
    )

    story_text = (
        f"{headline}\n"
        f"{subline}\n"
        "Jetzt probieren"
    )

    promo_text = (
        f"{headline} – {subline}. "
        "Ein Blick genügt und der Genuss beginnt."
    )

    return CaptionBundle(
        instagram_caption=instagram_caption,
        hashtags=hashtags,
        story_text=story_text,
        promo_text=promo_text,
    )