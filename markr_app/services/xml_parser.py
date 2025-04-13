from datetime import datetime
import logging
from lxml import etree
from markr_app.utils.errors import ValidationError

logger = logging.getLogger(__name__)

def parse_test_results(xml_content):
    """
    Parse XML content containing MCQ test results.
    
    Args:
        xml_content (str or bytes): XML content to parse
        
    Raises:
        ValidationError: If XML is malformed or invalid
    """
    try:
        # Parse XML with a secure parser to prevent XXE attacks
        parser = etree.XMLParser(resolve_entities=False)
        root = etree.fromstring(xml_content, parser=parser)
        
        # Verify root element is mcq-test-results
        if root.tag != 'mcq-test-results':
            raise ValidationError(f"Invalid root element: {root.tag}. Expected 'mcq-test-results'")
        
        # List to store parsed results
        results = []
        
        # Process each mcq-test-result element
        for result_elem in root.findall('mcq-test-result'):
            # Extract scanned-on timestamp if available
            scanned_on = result_elem.get('scanned-on')
            scanned_at = None
            if scanned_on:
                try:
                    scanned_at = datetime.fromisoformat(scanned_on.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Invalid timestamp format: {scanned_on}")
            
            # Extract required elements
            try:
                first_name = result_elem.findtext('first-name')
                last_name = result_elem.findtext('last-name')
                student_number = result_elem.findtext('student-number')
                test_id = result_elem.findtext('test-id')
                
                # Check if summary-marks element exists
                summary_elem = result_elem.find('summary-marks')
                if summary_elem is None:
                    raise ValidationError(f"Missing 'summary-marks' element for student {student_number}")
                
                # Extract marks attributes
                marks_available = summary_elem.get('available')
                marks_obtained = summary_elem.get('obtained')
                
                # All required fields must be present
                if any(field is None for field in [
                    first_name, last_name, student_number, test_id, marks_available, marks_obtained
                ]):
                    missing_fields = []
                    if first_name is None: missing_fields.append('first-name')
                    if last_name is None: missing_fields.append('last-name')
                    if student_number is None: missing_fields.append('student-number')
                    if test_id is None: missing_fields.append('test-id')
                    if marks_available is None: missing_fields.append('available attribute')
                    if marks_obtained is None: missing_fields.append('obtained attribute')
                    
                    raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
                
                # Try to convert marks to integers
                try:
                    marks_available = int(marks_available)
                    marks_obtained = int(marks_obtained)
                except ValueError:
                    raise ValidationError(f"Marks must be integers: available={marks_available}, obtained={marks_obtained}")
                
                # Validate marks if non-negative
                if marks_available < 0 or marks_obtained < 0:
                    raise ValidationError(f"Marks cannot be negative: available={marks_available}, obtained={marks_obtained}")
                
                # Add parsed result to list
                results.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'student_number': student_number,
                    'test_id': test_id,
                    'marks_available': marks_available,
                    'marks_obtained': marks_obtained,
                    'scanned_at': scanned_at
                })
                
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                raise ValidationError(f"Error extracting test result data: {str(e)}")
        
        # Ensure we found at least one result
        if not results:
            raise ValidationError("No valid test results found in XML document")
            
        return results
        
    except etree.XMLSyntaxError as e:
        raise ValidationError(f"Invalid XML syntax: {str(e)}")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Error parsing XML: {str(e)}")