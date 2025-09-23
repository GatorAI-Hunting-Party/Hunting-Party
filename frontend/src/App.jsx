import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import DocumentUpload from './components/DocumentUpload';
import DealList from './components/DealList';
import DealAnalysis from './components/DealAnalysis';
import MarketData from './components/MarketData';
import './App.css';

function App() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDeals();
  }, []);

  const fetchDeals = async () => {
    try {
      const response = await fetch('http://localhost:8000/deals');
      const data = await response.json();
      setDeals(data.deals || []);
    } catch (error) {
      console.error('Error fetching deals:', error);
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">
                  🏠 HuntingParty.ai
                </h1>
                <span className="ml-2 text-sm text-gray-500">
                  Real Estate Deal Analysis Platform
                </span>
              </div>
              <nav className="flex space-x-8">
                <Link
                  to="/"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Upload
                </Link>
                <Link
                  to="/deals"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Deals
                </Link>
                <Link
                  to="/market-data"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Market Data
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route
              path="/"
              element={
                <DocumentUpload
                  onUploadSuccess={() => {
                    fetchDeals();
                    setLoading(false);
                  }}
                  onUploadStart={() => setLoading(true)}
                />
              }
            />
            <Route
              path="/deals"
              element={<DealList deals={deals} onRefresh={fetchDeals} />}
            />
            <Route path="/deals/:dealId" element={<DealAnalysis />} />
            <Route path="/market-data" element={<MarketData />} />
          </Routes>
        </main>

        {/* Loading Overlay */}
        {loading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-700">Processing document...</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
