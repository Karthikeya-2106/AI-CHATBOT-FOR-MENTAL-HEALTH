CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life",
    "want to die", "can't go on", "no reason to live",
    "self harm", "hurt myself", "hopeless", "worthless"
]

HELPLINE = (
    "I'm really concerned about you. Please reach out immediately:\n"
    "iCall Helpline: 9152987821\n"
    "Vandrevala Foundation: 1860-2662-345 (24/7)\n"
    "You are not alone. A trained counselor can help right now."
)

SPECIALIST_MAP = {
    "neuro": "Neurologist",
    "brain": "Neurologist",
    "seizure": "Neurologist",
    "heart": "Cardiologist",
    "cardiac": "Cardiologist",
    "chest pain": "Cardiologist",
    "skin": "Dermatologist",
    "rash": "Dermatologist",
    "acne": "Dermatologist",
    "bone": "Orthopedist",
    "joint": "Orthopedist",
    "fracture": "Orthopedist",
    "eye": "Ophthalmologist",
    "vision": "Ophthalmologist",
    "stomach": "Gastroenterologist",
    "digestive": "Gastroenterologist",
    "vomit": "Gastroenterologist",
    "lungs": "Pulmonologist",
    "breathing": "Pulmonologist",
    "asthma": "Pulmonologist",
    "mental": "Psychiatrist",
    "depression": "Psychiatrist",
    "anxiety": "Psychiatrist",
    "teeth": "Dentist",
    "dental": "Dentist",
    "child": "Pediatrician",
    "kidney": "Nephrologist",
    "diabetes": "Endocrinologist",
    "thyroid": "Endocrinologist",
}

def check_crisis(text):
    text_lower = text.lower()
    for word in CRISIS_KEYWORDS:
        if word in text_lower:
            return True
    return False

def get_specialist(text):
    text_lower = text.lower()
    for keyword, specialist in SPECIALIST_MAP.items():
        if keyword in text_lower:
            return specialist
    return "General Physician"
