import logging
import numpy as np
from markr_app.models import TestResult

logger = logging.getLogger(__name__)

def calculate_aggregates(test_id):
    """
    Calculate aggregate statistics for a given test       
    Returns:
        dict: Dictionary containing aggregate statistics
    """
    
    # Get all results for the test ID
    results = TestResult.find_all_by_test_id(test_id)

    # Check if any results were found
    if not results:
        logger.warning(f"No results found for test ID: {test_id}")
        raise ValueError(f"No results found for test ID: {test_id}")
    
    # Extract marks obtained
    marks_obtained = [result.marks_obtained for result in results]

    # Find the max available marks for this test
    max_marks_available = max(result.mark_available for result in results)

    # Check if the max_marks_available is 0 to avoid division by 0
    if max_marks_available == 0:
        logger.warning(f"Maximum available marks is zero for test ID: {test_id}")
        raise ValueError(f"Maximum available marks is zero for test ID: {test_id}")
    
    # Calculate the aggregate stats
    count = len(marks_obtained)

    # Calculate mean & percentiles
    mean_marks = np.mean(marks_obtained)
    p25 = np.percentile(marks_obtained, 25)
    p50 = np.percentile(marks_obtained, 50)
    p75 = np.percentile(marks_obtained, 75)

    # calculate the min & max
    min_marks = np.min(marks_obtained)
    max_marks = np.max(marks_obtained)

    # Convert to percentages
    mean_percent = (mean_marks / max_marks_available) * 100.0
    p25_percent = (p25 / max_marks_available) * 100.0
    p50_percent = (p50 / max_marks_available) * 100.0
    p75_percent = (p75 / max_marks_available) * 100.0
    min_percent = (min_marks / max_marks_available) * 100.0
    max_percent = (max_marks / max_marks_available) * 100.0

    # Return the aggregate stats
    return {
        "mean": mean_percent,
        "count": count,
        "p25": p25_percent,
        "p75": p75_percent,
        "min": min_percent,
        "max": max_percent,
    }


