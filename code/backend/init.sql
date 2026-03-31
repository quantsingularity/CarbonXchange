-- CarbonXchange Database Initialization Script
-- Creates extensions and initial setup for PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_stat_statements for query monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Set timezone
SET timezone = 'UTC';

-- Create indexes that SQLAlchemy won't automatically create
-- (run after Flask-Migrate creates tables)

DO $$ 
BEGIN
    RAISE NOTICE 'CarbonXchange database initialized successfully';
END $$;
