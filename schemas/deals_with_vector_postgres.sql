-- Import pgVector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table with info + embedding vector
CREATE TABLE IF NOT EXISTS deal (
    id SERIAL PRIMARY KEY,

    asset_name VARCHAR(128) NOT NULL,

    street_address VARCHAR(128) NOT NULL,
    city VARCHAR(128) NOT NULL,
    state VARCHAR(128) NOT NULL,
    zip VARCHAR(9) NOT NULL,
    full_address TEXT GENERATED ALWAYS AS (street_address || ', ' || city || ', ' || state || ', ' || zip) STORED,

    total_units INTEGER NOT NULL,
    net_rentable_area DOUBLE PRECISION NOT NULL,
    current_occupancy DOUBLE PRECISION NOT NULL CHECK (current_occupancy >= 0 AND current_occupancy <= 1),

    embedding vector(256)
);

-- Initialize the index
CREATE INDEX IF NOT EXISTS deal_embedding ON deal
USING hnsw (embedding vector_cosine_ops);
