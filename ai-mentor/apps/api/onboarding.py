"""
onboarding.py - The "Mirror" Diagnostic Module

Implements the Pavel Bilskiy methodology for:
1. Driver Detection (Be Strong, Be Best, Please Others)
2. Script Pattern Detection (Until, After, Never, Always)
3. Core Wound Identification

This creates the User's "Psychological Profile" in Supabase.
"""

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


# --- Enums for Methodology ---
class Driver(str, Enum):
    BE_STRONG = "be_strong"
    BE_BEST = "be_best"
    PLEASE_OTHERS = "please_others"


class ScriptPattern(str, Enum):
    UNTIL = "until"      # "I can't relax until..."
    AFTER = "after"      # "If I'm happy today, I'll pay tomorrow..."
    NEVER = "never"      # "I'll never get what I want..."
    ALMOST = "almost"    # "I always stop right before finishing..."
    ALWAYS = "always"    # "Why does this always happen to me?"


class Injunction(str, Enum):
    DONT_EXIST = "dont_exist"
    DONT_BE_YOURSELF = "dont_be_yourself"
    DONT_BE_CHILD = "dont_be_child"
    DONT_GROW = "dont_grow"
    DONT_SUCCEED = "dont_succeed"
    DONT_DO = "dont_do"
    DONT_BE_IMPORTANT = "dont_be_important"
    DONT_BELONG = "dont_belong"
    DONT_BE_CLOSE = "dont_be_close"
    DONT_BE_HEALTHY = "dont_be_healthy"
    DONT_THINK = "dont_think"
    DONT_FEEL = "dont_feel"


# --- Onboarding Questions ---
DRIVER_QUESTIONS = [
    {
        "id": "failure_response",
        "question": "Imagine you just made a mistake at work or in a relationship. What is your immediate thought?",
        "options": [
            {"text": "I must fix this myself. I cannot show weakness.", "driver": Driver.BE_STRONG, "points": 2},
            {"text": "This is a disaster. I'm failing to be the best.", "driver": Driver.BE_BEST, "points": 2},
            {"text": "I hope they aren't mad at me. I need to fix their mood.", "driver": Driver.PLEASE_OTHERS, "points": 2},
        ]
    },
    {
        "id": "relief_source",
        "question": "What gives you the biggest sense of relief?",
        "options": [
            {"text": "Knowing I didn't ask anyone for help.", "driver": Driver.BE_STRONG, "points": 2},
            {"text": "Being recognized as superior or unique.", "driver": Driver.BE_BEST, "points": 2},
            {"text": "Knowing everyone around me is happy with me.", "driver": Driver.PLEASE_OTHERS, "points": 2},
        ]
    },
    {
        "id": "avoided_emotion",
        "question": "What feeling do you try hardest to avoid?",
        "options": [
            {"text": "Feeling weak or vulnerable.", "driver": Driver.BE_STRONG, "points": 2},
            {"text": "Feeling average or unnoticed.", "driver": Driver.BE_BEST, "points": 2},
            {"text": "Feeling guilty or causing conflict.", "driver": Driver.PLEASE_OTHERS, "points": 2},
        ]
    },
    {
        "id": "help_reaction",
        "question": "When someone offers you help, what's your first reaction?",
        "options": [
            {"text": "I feel uncomfortable and usually decline.", "driver": Driver.BE_STRONG, "points": 1},
            {"text": "I accept only if they're an expert I respect.", "driver": Driver.BE_BEST, "points": 1},
            {"text": "I worry I'm being a burden to them.", "driver": Driver.PLEASE_OTHERS, "points": 1},
        ]
    },
    {
        "id": "childhood_message",
        "question": "Which message did you receive most in childhood?",
        "options": [
            {"text": "Be tough. Don't cry. Handle it yourself.", "driver": Driver.BE_STRONG, "points": 2},
            {"text": "Be the best. Second place is first loser.", "driver": Driver.BE_BEST, "points": 2},
            {"text": "Don't upset others. Be nice. Keep the peace.", "driver": Driver.PLEASE_OTHERS, "points": 2},
        ]
    },
]

SCRIPT_PATTERN_QUESTIONS = [
    {
        "id": "happiness_delay",
        "question": "Which sentence sounds most like your inner voice?",
        "options": [
            {"text": "I can't relax until all my work is done.", "pattern": ScriptPattern.UNTIL},
            {"text": "If I laugh too much today, I'll pay for it with tears tomorrow.", "pattern": ScriptPattern.AFTER},
            {"text": "I often start things but lose interest just before finishing.", "pattern": ScriptPattern.ALMOST},
            {"text": "Why does this always happen to me? It's the same pattern again.", "pattern": ScriptPattern.ALWAYS},
        ]
    },
]


# --- Pydantic Models ---
class OnboardingAnswer(BaseModel):
    question_id: str
    selected_option_index: int


class OnboardingSubmission(BaseModel):
    user_id: str
    driver_answers: List[OnboardingAnswer]
    script_answer: OnboardingAnswer


class DiagnosisResult(BaseModel):
    driver: Driver
    driver_scores: dict
    script_pattern: ScriptPattern
    core_wound: str
    onboarding_completed: bool = True


# --- Scoring Logic ---
def calculate_driver(answers: List[OnboardingAnswer]) -> tuple[Driver, dict]:
    """Calculate primary driver from answers."""
    scores = {
        Driver.BE_STRONG: 0,
        Driver.BE_BEST: 0,
        Driver.PLEASE_OTHERS: 0,
    }
    
    for answer in answers:
        # Find the question
        question = next((q for q in DRIVER_QUESTIONS if q["id"] == answer.question_id), None)
        if not question:
            continue
        
        # Get selected option
        if 0 <= answer.selected_option_index < len(question["options"]):
            option = question["options"][answer.selected_option_index]
            scores[option["driver"]] += option["points"]
    
    # Get primary driver
    primary_driver = max(scores, key=scores.get)
    
    return primary_driver, {k.value: v for k, v in scores.items()}


def calculate_script_pattern(answer: OnboardingAnswer) -> ScriptPattern:
    """Determine script pattern from answer."""
    question = SCRIPT_PATTERN_QUESTIONS[0]  # We only have one for now
    if 0 <= answer.selected_option_index < len(question["options"]):
        return question["options"][answer.selected_option_index]["pattern"]
    return ScriptPattern.UNTIL  # Default


def get_core_wound(driver: Driver) -> str:
    """Map driver to core wound."""
    wounds = {
        Driver.BE_STRONG: "fear_of_vulnerability",
        Driver.BE_BEST: "fear_of_mediocrity",
        Driver.PLEASE_OTHERS: "fear_of_rejection",
    }
    return wounds.get(driver, "unknown")


def process_onboarding(submission: OnboardingSubmission) -> DiagnosisResult:
    """Process all onboarding answers and return diagnosis."""
    driver, driver_scores = calculate_driver(submission.driver_answers)
    script_pattern = calculate_script_pattern(submission.script_answer)
    core_wound = get_core_wound(driver)
    
    return DiagnosisResult(
        driver=driver,
        driver_scores=driver_scores,
        script_pattern=script_pattern,
        core_wound=core_wound,
        onboarding_completed=True
    )


# --- Driver-Specific Instructions for System Prompt ---
def get_driver_instructions(driver: str) -> str:
    """Get AI behavior instructions based on user's driver."""
    instructions = {
        "be_strong": """User has the "Be Strong" driver.
- They HATE asking for help. Do NOT offer "help" directly.
- Ask: "What resources do you need to solve this yourself?"
- Validate their strength, then gently challenge their isolation.
- They suppress emotions. Encourage them to feel vulnerability as strength.
- Key phrase: "True strength includes the courage to be vulnerable."
""",
        "be_best": """User has the "Be Best" driver.
- They fear being average or unnoticed.
- Acknowledge their ambition and achievements.
- Challenge them: "Does this achievement fuel you, or just feed the anxiety of falling behind?"
- They compare themselves constantly. Redirect to internal metrics.
- Key phrase: "You are enough, even without proving it."
""",
        "please_others": """User has the "Please Others" driver.
- They feel guilty saying "No" and fear conflict.
- Remind them: "Your boundaries protect your value."
- Never pressure them. Ask: "What do YOU want?"
- They prioritize others' needs over their own.
- Key phrase: "Disappointing others is safe. It doesn't mean you're bad."
""",
    }
    return instructions.get(driver, "No specific driver detected.")


def get_pattern_instructions(pattern: str) -> str:
    """Get AI behavior instructions based on user's script pattern."""
    instructions = {
        "until": """User has the "Until" pattern - they postpone happiness.
- Watch for: "I'll relax when..." / "After I finish..."
- Challenge: "What if you deserve rest NOW, not after?"
- They believe they must earn joy through work.
""",
        "after": """User has the "After" pattern - they fear punishment for joy.
- Watch for: "If I'm happy now, something bad will happen..."
- Challenge: "Joy doesn't require payment. It's not a transaction."
- They unconsciously self-sabotage after success.
""",
        "almost": """User has the "Almost" pattern - they stop before finishing.
- Watch for incomplete projects, last-minute pullouts.
- Challenge: "What are you afraid will happen if you fully succeed?"
- They have unconscious fear of success/visibility.
""",
        "always": """User has the "Always" pattern - they see repeating negative cycles.
- Watch for: "Why does this ALWAYS happen to me?"
- Challenge: "What's YOUR role in this pattern?"
- They feel victimized but unconsciously recreate scenarios.
""",
    }
    return instructions.get(pattern, "No specific pattern detected.")
