-- HuntingParty.ai Basic Schema
-- Database-agnostic schema for core metrics
-- Compatible with any SQL database

-- Create the main deals table
CREATE TABLE deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_name VARCHAR(255) NOT NULL,
    full_address TEXT NOT NULL,
    total_units INTEGER,
    net_rentable_area_sqft INTEGER,
    current_occupancy_percent DECIMAL(5,2),
    source_document VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO deals (asset_name, full_address, total_units, net_rentable_area_sqft, current_occupancy_percent, source_document) VALUES 
('Sunset Apartments', '123 Main Street, Austin, TX 78701', 150, 125000, 95.5, 'sunset_om.pdf'),
('Downtown Office Plaza', '456 Business Ave, Dallas, TX 75201', NULL, 75000, 88.2, 'office_om.pdf'),
('Riverside Complex', '789 River Road, Houston, TX 77002', 200, 180000, 92.8, 'riverside_om.pdf');
