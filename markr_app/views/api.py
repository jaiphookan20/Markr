from flask import Blueprint, request, jsonify
from markr_app.utils.errors import ValidationError
from markr_app.services.ingestion import process_test_results
from markr_app.services.aggregation import calculate_aggregates

api_bp = Blueprint('api', __name__)

@api_bp.route('/import', methods=['POST'])
def import_results():
    """Import XML test results Endpoint"""

    content_type = request.headers.get('Content-Type', '')
    
    if content_type != 'text/xml+markr':
        return jsonify({
            'error': 'Unsupported Media Type',
            'message': 'Expected Content-Type: text/xml+markr'
        }), 415
    
    # Get XML content from the request body
    xml_content = request.data
    if not xml_content:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Request body is empty'
        }), 400
    
    try:
        # Process the XML test results
        processed_count = process_test_results(xml_content)

        return jsonify({
            'success': True,
            'message': f"Successfully processed {processed_count} test results"
        }), 200
    except ValidationError as e:
        # Return validation error
        return jsonify({
            'error': 'Validation Error',
            'message': str(e)
        }), 400
    except Exception as e:
        # Return validation error
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occured while processing the test results'
        }), 500

@api_bp.route('/results/<test_id>/aggregate', methods=['GET'])
def get_aggregate_results(test_id):
    """ Get the aggregate results for a test
    
    Return a JSON object with the mean, count, p25, p50, p75 values
    """

    try:
        # Calculate aggregate statistics
        aggregates = calculate_aggregates(test_id)

        return jsonify(aggregates), 200

    except ValueError as e:
        # Return not found error
        return jsonify({
            'error': 'Not Found',
            'message': f"{str(e)}"
        }), 404
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': f"An error occured while calculating aggregates: {str(e)}"
        }), 500
    

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({"message": "OK"})

    
    