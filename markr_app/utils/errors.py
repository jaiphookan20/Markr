from flask import jsonify

class ValidationError(ValueError):
    """Exception raised for validation errors"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ZeroMarksError(Exception):
    """Exception raised when marks_available is zero"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def register_error_handlers(app):
    """Register error handlers for the app"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        response = jsonify({'error': 'Validation Error', 'message': str(error.message)})
        response.status_code = 400
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        response = jsonify({'error': 'Not Found', 'message': 'The requested resource was not found.'})
        response.status_code = 404
        return response
    
    @app.errorhandler(415)
    def handle_unsupported_media_type(error):
        response = jsonify({'error': 'Unsupported Media Type', 'message': 'The content type is not supported'})
        response.status_code = 415
        return response
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        response = jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred.'})
        response.status_code = 500
        return response

    

