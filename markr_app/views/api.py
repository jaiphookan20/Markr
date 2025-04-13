from flask import Blueprint, request, jsonify
from markr_app.utils.errors import ValidationError

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
def upload_test_results():
    """Import XML test results Endpoint"""

    # check content type
    if request.content_type != 'text/xml+makr':
        raise ValidationError('Content-Type must be text/xml+markr')
    
    # TODO: Implement XML validation, parsing & DB insertion
    return jsonify({"message": "Import endpoint"}), 501

@api_bp.route('/results/<test_id>/aggregate', methods=['GET'])
def get_aggregate_results(test_id):
    """ Get the aggregate results for a test
    
    Return a JSON object with the mean, count, p25, p50, p75 values
    """

    # TODO: Implement aggregation calculations
    return jsonify({"message": f"Aggregation for test {test_id} to be implemented"})
    

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({"message": "OK"})

    
    