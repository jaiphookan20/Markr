set -e  # Exit on error
 
 echo "Setting up test environment..."
 
 # Create test database if it doesn't exist
 echo "Setting up test database..."
 PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d postgres -c "
     SELECT COUNT(*) FROM pg_database WHERE datname = 'markrdb_test'
 " | grep -q 0 && \
 PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d postgres -c "
     CREATE DATABASE markrdb_test
 "
 
 echo "Test environment ready"