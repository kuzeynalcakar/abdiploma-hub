"""Shared mastery and confidence calculations for weakness map and practice."""

MASTERY_EXCELLENT = "excellent"
MASTERY_STRONG = "strong"
MASTERY_IMPROVING = "improving"
MASTERY_WEAK = "weak"
MASTERY_CRITICAL = "critical"
MASTERY_NOT_ATTEMPTED = "not_attempted"

CONFIDENCE_NOT_ATTEMPTED = "not_attempted"
CONFIDENCE_LOW = "low"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_HIGH = "high"

MASTERED_LEVELS = {MASTERY_EXCELLENT, MASTERY_STRONG}
WEAK_LEVELS = {MASTERY_WEAK, MASTERY_CRITICAL}


def mastery_level_for(accuracy: float, questions_attempted: int) -> str:
    if questions_attempted == 0:
        return MASTERY_NOT_ATTEMPTED
    if accuracy >= 90:
        return MASTERY_EXCELLENT
    if accuracy >= 75:
        return MASTERY_STRONG
    if accuracy >= 60:
        return MASTERY_IMPROVING
    if accuracy >= 40:
        return MASTERY_WEAK
    return MASTERY_CRITICAL


def mastery_label(level: str) -> str:
    labels = {
        MASTERY_EXCELLENT: "Excellent",
        MASTERY_STRONG: "Strong",
        MASTERY_IMPROVING: "Improving",
        MASTERY_WEAK: "Weak",
        MASTERY_CRITICAL: "Critical",
        MASTERY_NOT_ATTEMPTED: "Not Attempted",
    }
    return labels.get(level, level)


def confidence_level_for(questions_attempted: int) -> str:
    if questions_attempted == 0:
        return CONFIDENCE_NOT_ATTEMPTED
    if questions_attempted < 4:
        return CONFIDENCE_LOW
    if questions_attempted < 11:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_HIGH


def weakness_level_for(accuracy: float) -> str:
    """Legacy storage field on topic_performance; maps to mastery tier."""
    return mastery_level_for(accuracy, questions_attempted=1)
