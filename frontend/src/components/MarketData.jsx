import React, { useState } from 'react';
import axios from 'axios';

const MarketData = () => {
  const [location, setLocation] = useState('');
  const [propertyType, setPropertyType] = useState('multifamily');
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const propertyTypes = [
    { value: 'multifamily', label: 'Multifamily' },
    { value: 'office', label: 'Office' },
    { value: 'retail', label: 'Retail' },
    { value: 'industrial', label: 'Industrial' },
    { value: 'hotel', label: 'Hotel' },
    { value: 'mixed_use', label: 'Mixed Use' }
  ];

  const fetchMarketData = async () => {
    if (!location.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError(null);
    setMarketData(null);

    try {
      const response = await axios.get(
        `http://localhost:8000/market-data/${encodeURIComponent(location)}/${propertyType}`
      );
      setMarketData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch market data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Market Data Explorer
        </h2>
        <p className="text-gray-600">
          Get market data for specific locations and property types
        </p>
      </div>

      {/* Search Form */}
      <div className="card mb-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <input
              type="text"
              id="location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., Austin, TX or New York, NY"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="propertyType" className="block text-sm font-medium text-gray-700 mb-2">
              Property Type
            </label>
            <select
              id="propertyType"
              value={propertyType}
              onChange={(e) => setPropertyType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {propertyTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={fetchMarketData}
            disabled={loading}
            className="btn-primary w-full disabled:opacity-50"
          >
            {loading ? 'Fetching Data...' : 'Get Market Data'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="card border-red-200 bg-red-50 mb-6">
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            ❌ Error
          </h3>
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Market Data Results */}
      {marketData && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            Market Data for {location} - {propertyTypes.find(t => t.value === propertyType)?.label}
          </h3>

          {marketData.market_data && Object.keys(marketData.market_data).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(marketData.market_data).map(([key, value]) => (
                <div key={key} className="metric-card">
                  <div className="metric-value">
                    {typeof value === 'object' && value.value ? value.value : value}
                    {typeof value === 'object' && value.unit && (
                      <span className="metric-unit"> {value.unit}</span>
                    )}
                  </div>
                  <div className="metric-label">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No market data available</h3>
              <p className="text-gray-500">
                Market data for this location and property type is not currently available.
              </p>
            </div>
          )}

          {/* Metadata */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Data Source Information</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <div>Extraction Method: {marketData.metadata?.extraction_method || 'N/A'}</div>
              <div>Extraction Date: {marketData.metadata?.extraction_date || 'N/A'}</div>
              <div>Confidence Score: {marketData.metadata?.confidence_score ? `${(marketData.metadata.confidence_score * 100).toFixed(1)}%` : 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Sample Locations */}
      <div className="card mt-6">
        <h3 className="text-lg font-semibold mb-4">Sample Locations</h3>
        <p className="text-gray-600 mb-4">Try these sample locations to see market data:</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            'Austin, TX',
            'Denver, CO',
            'Nashville, TN',
            'Phoenix, AZ',
            'Atlanta, GA',
            'Charlotte, NC',
            'Dallas, TX',
            'Houston, TX'
          ].map((sampleLocation) => (
            <button
              key={sampleLocation}
              onClick={() => {
                setLocation(sampleLocation);
                fetchMarketData();
              }}
              className="text-sm px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              {sampleLocation}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketData;
