import pytest
from datetime import datetime, timezone
from markr_app.models import TestResult

class TestAggregation:
    def test_aggregation_multiple_results(self, client, session):
        
        """Test successful aggregation with multiple results"""
        
        # Create test data (Sample generated by AI)
        test_data = [
            TestResult(student_number='S12345', test_id='TEST001', first_name='John', last_name='Doe',
                      marks_obtained=15, marks_available=20, 
                      scanned_at=datetime(2022, 10, 1, 12, 0, tzinfo=timezone.utc)),
            TestResult(student_number='S67890', test_id='TEST001', first_name='Jane', last_name='Smith',
                      marks_obtained=18, marks_available=20,
                      scanned_at=datetime(2022, 10, 1, 12, 30, tzinfo=timezone.utc)),
            TestResult(student_number='S24680', test_id='TEST001', first_name='Alice', last_name='Johnson',
                      marks_obtained=12, marks_available=20,
                      scanned_at=datetime(2022, 10, 1, 13, 0, tzinfo=timezone.utc)),
            TestResult(student_number='S13579', test_id='TEST001', first_name='Bob', last_name='Brown',
                      marks_obtained=20, marks_available=20,
                      scanned_at=datetime(2022, 10, 1, 13, 30, tzinfo=timezone.utc)),
            TestResult(student_number='S97531', test_id='TEST001', first_name='Charlie', last_name='Wilson',
                      marks_obtained=10, marks_available=20,
                      scanned_at=datetime(2022, 10, 1, 14, 0, tzinfo=timezone.utc)),
        ]
        
        # Add test data to the database
        for result in test_data:
            session.add(result)
        session.commit()
        
        # Send a request to the aggregation endpoint
        response = client.get('/results/TEST001/aggregate')
        
        # Check response status code and content
        assert response.status_code == 200
        
        # Check the aggregate values
        aggregates = response.json
        assert 'mean' in aggregates
        assert 'count' in aggregates
        assert 'p25' in aggregates
        assert 'p50' in aggregates
        assert 'p75' in aggregates
        assert 'min' in aggregates
        assert 'max' in aggregates
        
        # Mean of [15, 18, 12, 20, 10] as percentage of 20
        assert aggregates['mean'] == 75.0 
        assert aggregates['count'] == 5
        assert aggregates['min'] == 50.0  
        assert aggregates['max'] == 100.0  
        
        # Percentiles
        assert aggregates['p25'] == 60.0  
        assert aggregates['p50'] == 75.0  
        assert aggregates['p75'] == 90.0  
    
    def test_aggregation_test_not_found(self, client, session):
        """Test aggregation when the test ID doesn't exist"""
        # Send a request for a non-existent test ID
        response = client.get('/results/NAN/aggregate')
        
        # Check response status code and content
        assert response.status_code == 404
        assert 'error' in response.json
        assert 'Not Found' in response.json['error']
        assert 'No results found for test ID' in response.json['message']
    
    def test_aggregation_single_result(self, client, session):
        """Test aggregation with a single result."""
        # Create a single test result
        result = TestResult(student_number='S12345', test_id='TEST002', first_name='John', last_name='Doe',
                           marks_obtained=15, marks_available=20,
                           scanned_at=datetime(2022, 10, 1, 12, 0, tzinfo=timezone.utc))
        session.add(result)
        session.commit()
        
        # Send a request to the aggregation endpoint
        response = client.get('/results/TEST002/aggregate')
        
        # Check response status code and content
        assert response.status_code == 200
        
        # Check the aggregate values
        aggregates = response.json
        assert aggregates['count'] == 1
        assert aggregates['mean'] == 75.0
        assert aggregates['min'] == 75.0
        assert aggregates['max'] == 75.0
        assert aggregates['p25'] == 75.0
        assert aggregates['p50'] == 75.0
        assert aggregates['p75'] == 75.0
    
    def test_aggregation_zero_marks_available(self, client, session):
        """Test aggregation when marks_available is zero."""
        # Create a test result with marks_available = 0
        result = TestResult(student_number='S12345', test_id='TEST003', first_name='John', last_name='Doe',
                           marks_obtained=0, marks_available=0,
                           scanned_at=datetime(2022, 10, 1, 12, 0, tzinfo=timezone.utc))
        session.add(result)
        session.commit()
        
        # Send a request to the aggregation endpoint
        response = client.get('/results/TEST003/aggregate')
        
        # Check response status code and content
        assert response.status_code == 500
        assert 'error' in response.json
        assert 'Internal Server Error' in response.json['error']
        assert 'Maximum available marks is zero' in response.json['message']
    
    def test_aggregation_nonexistent_test(self, client):
        """Test aggregation endpoint for a non-existent test """
        
        # Get aggregates for non-existent test
        response = client.get('/results/NAN/aggregate')
        
        # Check response
        assert response.status_code == 404
        assert 'Not Found' in response.json['error']