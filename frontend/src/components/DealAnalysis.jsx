import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const DealAnalysis = () => {
  const { dealId } = useParams();
  const [dealData, setDealData] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDealData();
  }, [dealId]);

  const fetchDealData = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/deals/${dealId}`);
      setDealData(response.data);
    } catch (err) {
      setError('Failed to fetch deal data');
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      const response = await axios.post(`http://localhost:8000/analyze/${dealId}`);
      setAnalysisResult(response.data);
    } catch (err) {
      setError('Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'flag-high';
      case 'medium': return 'flag-medium';
      case 'low': return 'flag-low';
      default: return 'flag-medium';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high': return '🚨';
      case 'medium': return '⚠️';
      case 'low': return 'ℹ️';
      default: return '⚠️';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-700">Loading deal data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
        <p className="text-gray-500">{error}</p>
      </div>
    );
  }

  if (!dealData) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Deal not found</h3>
        <p className="text-gray-500">The requested deal could not be found.</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Deal Analysis</h2>
          <p className="text-gray-600">Deal ID: {dealId}</p>
        </div>
        <button
          onClick={runAnalysis}
          disabled={analyzing}
          className="btn-primary disabled:opacity-50"
        >
          {analyzing ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {/* Deal Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="metric-card">
          <div className="metric-value">
            ${dealData.financial_metrics?.purchase_price?.toLocaleString() || 'N/A'}
          </div>
          <div className="metric-label">Purchase Price</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-value">
            {dealData.financial_metrics?.current_occupancy?.toFixed(1) || 'N/A'}%
          </div>
          <div className="metric-label">Current Occupancy</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-value">
            {dealData.investment_metrics?.entry_cap_rate?.toFixed(1) || 'N/A'}%
          </div>
          <div className="metric-label">Entry Cap Rate</div>
        </div>
      </div>

      {/* Property Information */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Property Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="font-medium">Address:</span> {dealData.property_info?.address || 'N/A'}
          </div>
          <div>
            <span className="font-medium">City:</span> {dealData.property_info?.city || 'N/A'}
          </div>
          <div>
            <span className="font-medium">State:</span> {dealData.property_info?.state || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Property Type:</span> {dealData.property_info?.property_type || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Total Sq Ft:</span> {dealData.property_info?.total_sqft?.toLocaleString() || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Year Built:</span> {dealData.property_info?.year_built || 'N/A'}
          </div>
        </div>
      </div>

      {/* Financial Metrics */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Financial Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="font-medium">T-12 Revenue:</span> ${dealData.financial_metrics?.t12_revenue?.toLocaleString() || 'N/A'}
          </div>
          <div>
            <span className="font-medium">T-12 Expenses:</span> ${dealData.financial_metrics?.t12_expenses?.toLocaleString() || 'N/A'}
          </div>
          <div>
            <span className="font-medium">T-12 NOI:</span> ${dealData.financial_metrics?.t12_noi?.toLocaleString() || 'N/A'}
          </div>
          <div>
            <span className="font-medium">Rent per Sq Ft:</span> ${dealData.financial_metrics?.rent_per_sqft || 'N/A'}
          </div>
        </div>
      </div>

      {/* Debt Information */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Debt Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="font-medium">Loan Amount:</span> ${dealData.debt_info?.loan_amount?.toLocaleString() || 'N/A'}
          </div>
          <div>
            <span className="font-medium">LTV Ratio:</span> {dealData.debt_info?.ltv_ratio || 'N/A'}%
          </div>
          <div>
            <span className="font-medium">Interest Rate:</span> {dealData.debt_info?.interest_rate || 'N/A'}%
          </div>
          <div>
            <span className="font-medium">DSCR:</span> {dealData.debt_info?.dscr || 'N/A'}
          </div>
        </div>
      </div>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Analysis Results</h3>
          
          {/* Risk Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Overall Risk Score</span>
              <span className={`text-lg font-bold ${
                analysisResult.risk_score >= 0.7 ? 'text-red-600' :
                analysisResult.risk_score >= 0.4 ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {(analysisResult.risk_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  analysisResult.risk_score >= 0.7 ? 'bg-red-500' :
                  analysisResult.risk_score >= 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${analysisResult.risk_score * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Summary */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Summary</h4>
            <p className="text-gray-700 whitespace-pre-line">{analysisResult.summary}</p>
          </div>

          {/* Flags */}
          {analysisResult.flags && analysisResult.flags.length > 0 && (
            <div>
              <h4 className="font-medium mb-4">Issues Found</h4>
              <div className="space-y-3">
                {analysisResult.flags.map((flag, index) => (
                  <div key={index} className={`p-4 rounded-lg border ${getSeverityColor(flag.severity)}`}>
                    <div className="flex items-start">
                      <span className="text-lg mr-2">{getSeverityIcon(flag.severity)}</span>
                      <div className="flex-1">
                        <div className="font-medium">{flag.metric}</div>
                        <div className="text-sm mt-1">{flag.reason}</div>
                        {flag.gp_value && (
                          <div className="text-sm mt-1">
                            GP Value: {flag.gp_value}
                            {flag.market_value && ` | Market Value: ${flag.market_value}`}
                            {flag.variance && ` | Variance: ${(flag.variance * 100).toFixed(1)}%`}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DealAnalysis;
