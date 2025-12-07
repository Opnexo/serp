-- SimpleERP Database Initialization
-- Creates schemas for each module

-- Core schemas
CREATE SCHEMA IF NOT EXISTS common;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS crm;

-- Future module schemas (uncomment as needed)
-- CREATE SCHEMA IF NOT EXISTS invoicing;
-- CREATE SCHEMA IF NOT EXISTS sales;
-- CREATE SCHEMA IF NOT EXISTS products;
-- CREATE SCHEMA IF NOT EXISTS procurement;
-- CREATE SCHEMA IF NOT EXISTS inventory;
-- CREATE SCHEMA IF NOT EXISTS logistics;

-- Grant privileges to serp user
GRANT ALL PRIVILEGES ON SCHEMA common TO serp;
GRANT ALL PRIVILEGES ON SCHEMA users TO serp;
GRANT ALL PRIVILEGES ON SCHEMA crm TO serp;

-- Set search path to include all schemas
ALTER DATABASE serp SET search_path TO public, common, users, crm;

-- Log success
DO $$
BEGIN
    RAISE NOTICE 'SimpleERP schemas created successfully!';
END $$;
