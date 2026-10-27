"""A simple campus chatbot. The FAQ details are fictional examples."""
import re

MODEL = "gemini-3.5-flash-lite"

# Each rule contains matching words and one fixed answer.
FAQS = [
    (("library",), "Demo: The library opens Monday-Friday, 08:00-17:00."),
    (("registration", "register", "enrolment"), "Demo: Register through the Student Portal in the first two weeks of the semester."),
    (("fees", "payment", "tuition"), "Demo: Pay by bank transfer or card. Contact accounts@example.org for help."),
    (("exam", "exams", "attendance"), "Demo: You need 80% attendance. Bring your student ID and arrive 15 minutes early."),
    (("it support", "helpdesk", "wifi"), "Demo: Contact helpdesk@example.org or visit Room A102, Monday-Friday, 09:00-16:00."),
]


def reply(question, client=None):
    if not question.strip():
        return "Please enter a question."

    # Spaces around words prevent 'exam' from matching 'example'.
    text = " " + " ".join(re.findall(r"\w+", question.lower())) + " "
    for keywords, answer in FAQS:
        if any(" " + word + " " in text for word in keywords):
            return answer

    if client is None:
        return "Add a Gemini API key when starting the chatbot to answer other questions."
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=question,
            config={"system_instruction": "You are a helpful study assistant. Keep answers brief. Do not invent campus policies or contact details."},
        )
        return (response.text or "").strip() or "No answer received. Please try again."
    except Exception as error:
        # Show a useful category, never the raw error (which can contain secrets).
        detail = str(getattr(error, "message", error)).lower()
        if "leaked" in detail:
            return "Gemini rejected a leaked key. Create a new key in Google AI Studio."
        if "api key not valid" in detail or "api_key_invalid" in detail:
            return "Gemini rejected the API key (400). Copy a complete key from Google AI Studio."
        if "certificate_verify_failed" in detail:
            return "AI connection failed: certificate verification. Check your computer's trusted certificates or network proxy."
        messages = {
            400: "Gemini rejected the request (400). Check the model and your account settings.",
            401: "Gemini authentication failed (401). Replace the API key in the sidebar.",
            403: "Gemini access denied (403). Check the key's API permissions and restrictions in Google AI Studio.",
            404: "Gemini model unavailable (404). Select a model available to your account.",
            429: "Gemini quota or rate limit reached (429). Check project usage and quota in Google AI Studio.",
            503: "Gemini is busy (503). Please try again shortly.",
        }
        return messages.get(getattr(error, "code", None), "AI is unavailable: a connection or SDK error occurred. Check your internet connection and restart the app.")
