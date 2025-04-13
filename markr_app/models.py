from datetime import datetime, timezone
from markr_app.database import db

class TestResult(db.Model):
    """Model for storing the test results"""
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_number = db.Column(db.String(50), nullable=False, index=True)
    test_id = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    marks_obtained = db.Column(db.Integer, nullable=False)
    marks_available = db.Column(db.Integer, nullable=False)
    scanned_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), 
                          default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Ensure uniqueness through student_number + test_id combination
    __table_args__ = (
        db.UniqueConstraint('student_number', 'test_id', name='uix_student_test')
    )

    def __repr__(self):
        """String representation of TestResult object"""
        return f"<TestResult(student={self.student_number}, test={self.test_id}, " \
               f"marks={self.marks_obtained}/{self.marks_available})>"
    
@classmethod
def find_by_student_and_test(cls, student_number, test_id):
    """Find test result through student number and test ID"""
    return cls.query.filter_by(
        student_number=student_number,
        test_id=test_id
    ).first()

@classmethod
def find_all_by_test_id(cls, test_id):
    """Find all test results for a specific test ID"""
    return cls.query.filter_by(test_id=test_id).all()
        