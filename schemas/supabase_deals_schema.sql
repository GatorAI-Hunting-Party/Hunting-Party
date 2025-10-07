-- HuntingParty.ai Supabase Schema
-- Optimized for Supabase PostgreSQL with your 5 core metrics

-- Create the main deals table
CREATE TABLE deals (
    id BIGSERIAL PRIMARY KEY,
    asset_name TEXT NOT NULL,
    full_address TEXT NOT NULL,
    total_units INTEGER,
    net_rentable_area_sqft INTEGER,
    current_occupancy_percent NUMERIC(5,2),
    source_document TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create an updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_deals_updated_at 
    BEFORE UPDATE ON deals 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO deals (asset_name, full_address, total_units, net_rentable_area_sqft, current_occupancy_percent, source_document) VALUES 
('Sunset Apartments', '123 Main Street, Austin, TX 78701', 150, 125000, 95.5, 'sunset_om.pdf'),
('Downtown Office Plaza', '456 Business Ave, Dallas, TX 75201', NULL, 75000, 88.2, 'office_om.pdf'),
('Riverside Complex', '789 River Road, Houston, TX 77002', 200, 180000, 92.8, 'riverside_om.pdf');

-- Enable Row Level Security (RLS) for security
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations for authenticated users
-- (You can modify this based on your security needs)
CREATE POLICY "Allow all operations for authenticated users" ON deals
    FOR ALL USING (auth.role() = 'authenticated');

-- Create indexes for better performance
CREATE INDEX idx_deals_asset_name ON deals(asset_name);
CREATE INDEX idx_deals_created_at ON deals(created_at);
CREATE INDEX idx_deals_occupancy ON deals(current_occupancy_percent);
