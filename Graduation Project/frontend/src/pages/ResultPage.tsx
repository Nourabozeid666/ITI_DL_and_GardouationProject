import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { PredictionResponse, PredictionRequest } from '../types/prediction';
import {
  formatIndianPrice,
  sqftToSqm,
  calculatePricePerSqft,
} from '../utils/formatters';

interface LocationState {
  result?: PredictionResponse;
  request?: PredictionRequest;
}

export const ResultPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as LocationState | undefined;
  const [copied, setCopied] = useState(false);

  const result = state?.result;
  const request = state?.request || result?.features_used;

  if (!result || !request) {
    return (
      <div className="card empty-result-card">
        <div className="empty-icon">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        </div>
        <h2>No Prediction Data Available</h2>
        <p>Please enter property specifications on the home page to get an estimated valuation.</p>
        <Link to="/" className="btn btn-primary">
          Go to Valuation Form
        </Link>
      </div>
    );
  }

  const formattedPrice =
    result.formatted_price || formatIndianPrice(result.predicted_price);
  const pricePerSqft = calculatePricePerSqft(
    result.predicted_price,
    request.carpet_area_sqft
  );

  const handleCopySummary = () => {
    const text = `Property Valuation Estimate: ${formattedPrice}\nLocation: ${request.location}\nCarpet Area: ${request.carpet_area_sqft} sq.ft. (${sqftToSqm(request.carpet_area_sqft)} m²)\nFloor: ${request.floor_num === 0 ? 'Ground' : request.floor_num}\nBathrooms: ${request.bathroom} | Balconies: ${request.balcony}\nFurnishing: ${request.furnishing} | Ownership: ${request.ownership}\nTransaction: ${request.transaction} | Facing: ${request.facing}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="result-page-wrapper">
      {/* Back Button */}
      <div className="page-nav-bar">
        <button
          type="button"
          onClick={() => navigate('/')}
          className="btn-back"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          <span>Back to Estimator</span>
        </button>
      </div>

      {/* Main Result Card */}
      <div className="card valuation-hero-card">
        <div className="valuation-badge">Estimated Market Price</div>
        <div className="valuation-price-display">
          <span className="price-tag">{formattedPrice}</span>
        </div>
        <p className="valuation-subtext">
          Based on regression inference across property features in <strong>{request.location}</strong>
        </p>

        {/* Quick Highlights */}
        <div className="valuation-highlights-grid">
          <div className="highlight-item">
            <span className="highlight-label">Est. Price / sqft</span>
            <span className="highlight-value">{pricePerSqft}</span>
          </div>
          <div className="highlight-item">
            <span className="highlight-label">Carpet Area</span>
            <span className="highlight-value">
              {request.carpet_area_sqft} sqft <span className="sub-unit">({sqftToSqm(request.carpet_area_sqft)} m²)</span>
            </span>
          </div>
          <div className="highlight-item">
            <span className="highlight-label">Floor</span>
            <span className="highlight-value">
              {request.floor_num === 0 ? 'Ground Floor' : `Floor ${request.floor_num}`}
            </span>
          </div>
        </div>
      </div>

      {/* Property Specifications Summary */}
      <div className="card specs-card">
        <div className="specs-header">
          <h3 className="specs-title">Property Parameters Used in Prediction</h3>
          <button
            type="button"
            className="btn-copy"
            onClick={handleCopySummary}
          >
            {copied ? '✓ Copied to Clipboard!' : 'Copy Summary'}
          </button>
        </div>

        <div className="specs-grid">
          <div className="spec-row">
            <span className="spec-name">Location / Area</span>
            <span className="spec-value badge badge-blue">{request.location}</span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Carpet Area</span>
            <span className="spec-value">{request.carpet_area_sqft} sq. ft.</span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Floor Level</span>
            <span className="spec-value">
              {request.floor_num === 0 ? 'Ground (0)' : `Floor ${request.floor_num}`}
            </span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Bathrooms</span>
            <span className="spec-value">{request.bathroom}</span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Balconies</span>
            <span className="spec-value">{request.balcony}</span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Furnishing</span>
            <span className="spec-value badge badge-gray">{request.furnishing}</span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Transaction Type</span>
            <span className="spec-value badge badge-gray">{request.transaction}</span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Ownership</span>
            <span className="spec-value badge badge-gray">{request.ownership}</span>
          </div>
          <div className="spec-row">
            <span className="spec-name">Facing Direction</span>
            <span className="spec-value badge badge-gray">{request.facing}</span>
          </div>
        </div>

        <div className="result-actions">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn btn-primary"
          >
            Estimate Another Property
          </button>
        </div>
      </div>
    </div>
  );
};
