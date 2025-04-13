import pytest
from markr_app.models import TestResult

class TestImport:
    def test_successful_import_single(self, client, valid_xml_single, session):
        """Test importing a single test result successfully."""
        # Send a request to the import endpoint
        response = client.post('/import', 
                              data=valid_xml_single, 
                              headers={'Content-Type': 'text/xml+markr'})
        
        # Check response status code and content
        assert response.status_code == 200
        assert response.json['success'] is True
        assert '1 test' in response.json['message']
        
        # Verify the data was saved to the database
        result = TestResult.query.filter_by(student_number='S12345', test_id='TEST001').first()
        assert result is not None
        assert result.first_name == 'John' 
        assert result.last_name == 'Doe'
        assert result.marks_obtained == 15
        assert result.marks_available == 20
    
    def test_successful_import_multiple(self, client, valid_xml_multiple, session):
        """Test importing multiple test results successfully."""
        # Send a request to the import endpoint
        response = client.post('/import', 
                              data=valid_xml_multiple, 
                              headers={'Content-Type': 'text/xml+markr'})
        
        # Check response status code and content
        assert response.status_code == 200
        assert response.json['success'] is True
        
        # Verify the data was saved to the database
        results = TestResult.query.filter_by(test_id='TEST001').all()
        assert len(results) == 3
        
        # Verify the individual results
        result1 = TestResult.query.filter_by(student_number='S12345').first()
        assert result1 is not None
        assert result1.marks_obtained == 15
        
        result2 = TestResult.query.filter_by(student_number='S67890').first()
        assert result2 is not None
        assert result2.marks_obtained == 18
        
        result3 = TestResult.query.filter_by(student_number='S24680').first()
        assert result3 is not None
        assert result3.marks_obtained == 12
    
    def test_import_duplicates_within_file(self, client, xml_with_duplicates, session):
        """Test importing XML with duplicate student records within the same file."""
        # Send a request to the import endpoint
        response = client.post('/import', 
                              data=xml_with_duplicates, 
                              headers={'Content-Type': 'text/xml+markr'})
        
        # Check response status code and content
        assert response.status_code == 200
        assert response.json['success'] is True
        
        # Only one record should be created
        results = TestResult.query.filter_by(student_number='S12345', test_id='TEST001').all()
        assert len(results) == 1
        
        # The record should have the higher marks (18 instead of 15)
        assert len(results) > 0  # Ensure we have at least one result
        assert results[0].marks_obtained == 18
        
    def test_import_invalid_xml_syntax(self, client, invalid_xml_syntax, session):
        """Test importing XML with invalid syntax."""
        # Send a request to the import endpoint
        response = client.post('/import', 
                              data=invalid_xml_syntax, 
                              headers={'Content-Type': 'text/xml+markr'})
        
        # Check response status code and content
        assert response.status_code == 400
        assert 'error' in response.json
        assert 'Invalid XML syntax' in response.json['message']
        
        # Verify no data was saved to the database
        results = TestResult.query.all()
        assert len(results) == 0
    
    def test_import_missing_fields(self, client, invalid_xml_missing_fields, session):
        """Test importing XML with missing required fields."""
        # Send a request to the import endpoint
        response = client.post('/import', 
                              data=invalid_xml_missing_fields, 
                              headers={'Content-Type': 'text/xml+markr'})
        
        # Check response status code and content
        assert response.status_code == 400
        assert 'error' in response.json
        assert 'Missing required fields' in response.json['message']
        
        # Verify no data was saved to the database
        results = TestResult.query.all()
        assert len(results) == 0
    
    def test_import_incorrect_content_type(self, client, valid_xml_single, session):
        """Test importing with incorrect content type."""
        # Send a request with wrong content type
        response = client.post('/import', 
                              data=valid_xml_single, 
                              headers={'Content-Type': 'application/xml'})
        
        # Check response status code and content
        assert response.status_code == 415
        assert 'error' in response.json
        assert 'Unsupported Media Type' in response.json['error']
        
        # Verify no data was saved to the database
        results = TestResult.query.all()
        assert len(results) == 0