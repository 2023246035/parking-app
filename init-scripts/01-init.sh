#!/bin/bash
# Database initialization script for ParkMyCar
# This runs automatically when PostgreSQL container starts for the first time

set -e

echo "Initializing ParkMyCar database..."

# The database is already created by POSTGRES_DB environment variable
# This script can be used for additional initialization if needed

# Create extensions if needed
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable UUID extension if needed
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Grant necessary permissions
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOSQL

echo "Database initialization completed successfully!"
