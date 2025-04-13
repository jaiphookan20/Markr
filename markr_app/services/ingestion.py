from datetime import datetime, timezone
import logging
from markr_app.database import db
from markr_app.models import TestResult
from markr_app.services.xml_parser import parse_test_results
from markr_app.utils.errors import ValidationError

logger = logging.getLogger(__name__)

def process_test_results(xml_content):
    """
    Process test results from XML content
            
    Raises:
        ValidationError: If XML content is invalid or processing fails
    """
    # Parse XML to extract test results
    parsed_results = parse_test_results(xml_content)
    
    # Track how many results were processed
    processed_count = 0
    
    try:
        # Process each result
        for result_data in parsed_results:
            student_number = result_data['student_number']
            test_id = result_data['test_id']
            
            # Check if result already exists
            existing_result = TestResult.find_by_student_and_test(student_number, test_id)
            
            if existing_result:
                # If the new result has a higher score, update the existing record
                if result_data['marks_obtained'] > existing_result.marks_obtained:
                    existing_result.first_name = result_data['first_name']
                    existing_result.last_name = result_data['last_name']
                    existing_result.marks_obtained = result_data['marks_obtained']
                    existing_result.marks_available = max(existing_result.marks_available, result_data['marks_available'])
                    existing_result.scanned_at = result_data['scanned_at']
                    existing_result.updated_at = datetime.now(timezone.utc)
                    logger.info(f"Updated result for student {student_number}, test {test_id}")
                    processed_count += 1
                else:
                    logger.info(f"Skipped result for student {student_number}, test {test_id}: existing score is higher")
            else:
                # Create a new result record
                new_result = TestResult(
                    student_number=student_number,
                    test_id=test_id,
                    first_name=result_data['first_name'],
                    last_name=result_data['last_name'],
                    marks_obtained=result_data['marks_obtained'],
                    marks_available=result_data['marks_available'],
                    scanned_at=result_data['scanned_at']
                )
                db.session.add(new_result)
                logger.info(f"Inserted new result for student {student_number}, test {test_id}")
                processed_count += 1
        
        # Commit all changes in a single transaction
        db.session.commit()
        logger.info(f"Successfully processed {processed_count} test results")
        return processed_count
        
    except Exception as e:
        # Roll back transaction on error
        db.session.rollback()
        logger.error(f"Error processing test results: {str(e)}")
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Failed to process test results: {str(e)}")