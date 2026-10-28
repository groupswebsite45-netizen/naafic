from typing import Tuple
from decimal import Decimal


def calculate_grade(marks: Decimal, max_marks: Decimal) -> Tuple[str, str, float]:
    """
    Calculate grade, evaluation remark, and percentage for an assessment.
    
    Authoritative Hawlwadaag School Grading Scale:
    - 90% - 100%: A+ (Outstanding Performance)
    - 80% - 89.99%: A (Excellent Mastery)
    - 70% - 79.99%: B (Very Good Progress)
    - 60% - 69.99%: C (Good / Satisfactory)
    - 50% - 59.99%: D (Pass / Acceptable)
    - Below 50%: F (Fail / Needs Improvement)
    """
    if max_marks <= 0:
        return "F", "Invalid maximum marks", 0.0

    percentage = round((float(marks) / float(max_marks)) * 100.0, 2)

    if percentage >= 90.0:
        return "A+", "Outstanding performance", percentage
    elif percentage >= 80.0:
        return "A", "Excellent mastery", percentage
    elif percentage >= 70.0:
        return "B", "Very good progress", percentage
    elif percentage >= 60.0:
        return "C", "Satisfactory", percentage
    elif percentage >= 50.0:
        return "D", "Pass", percentage
    else:
        return "F", "Needs Improvement", percentage


def is_passing(marks: Decimal, pass_marks: Decimal) -> bool:
    """Evaluate whether student obtained passing marks."""
    return marks >= pass_marks
