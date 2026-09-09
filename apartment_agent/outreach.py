from __future__ import annotations

from .models import Listing, Requirements


def draft_message(listing: Listing, req: Requirements, your_name: str = "[Your name]") -> str:
    """Draft a personalized inquiry message for a listing. This never sends anything --
    it's meant to be reviewed and sent by a human via email, the listing site's contact
    form, or Facebook Messenger."""
    greeting = f"Hi{f' {listing.contact_name}' if listing.contact_name else ''},"

    where = listing.address or listing.title
    price_part = f" for ${listing.price:g}/mo" if listing.price is not None else ""
    intro = f"I saw your listing for {where}{price_part} and I'm very interested."

    questions = ["Is this unit still available?"]
    if req.pet_friendly is True and listing.pet_friendly is None:
        questions.append("Is it pet friendly?")
    if req.move_in_by and not listing.available_date:
        questions.append("What's the earliest move-in date?")
    if listing.price is None:
        questions.append("What is the monthly rent, and what's included (utilities, parking, etc.)?")
    questions.extend(req.extra_questions)

    question_lines = "\n".join(f"- {q}" for q in questions)

    body = (
        f"{greeting}\n\n"
        f"{intro} A few quick questions:\n"
        f"{question_lines}\n\n"
        "Could you let me know? Thanks so much!\n\n"
        f"{your_name}"
    )

    subject = f"Inquiry about {listing.title}"
    return f"Subject: {subject}\n\n{body}"
