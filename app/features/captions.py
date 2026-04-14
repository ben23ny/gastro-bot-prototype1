from app.core.schemas import CaptionResult


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


def build_caption_bundle(headline: str, subline: str, style_profile: str) -> CaptionResult:
    hashtags = " ".join(STYLE_HASHTAGS.get(style_profile, STYLE_HASHTAGS["luxury"]))

    return CaptionResult(
        instagram_caption=(
            f"{headline}\n\n"
            f"{subline}\n\n"
            "Mit Liebe zum Detail serviert und perfekt für den nächsten Genussmoment. "
            "Jetzt entdecken, genießen und direkt Lust auf mehr bekommen."
        ),
        hashtags=hashtags,
        story_text=f"{headline}\n{subline}\nJetzt probieren",
        promo_text=f"{headline} – {subline}. Ein Blick genügt und der Genuss beginnt.",
    )