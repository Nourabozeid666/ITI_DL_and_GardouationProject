import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PredictionForm } from '../components/PredictionForm';
import { getPricePrediction } from '../api/predictionClient';
import { PredictionRequest } from '../types/prediction';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handlePredictionSubmit = async (formData: PredictionRequest) => {
    setLoading(true);
    setErrorMessage(null);

    try {
      const response = await getPricePrediction(formData);
      navigate('/result', {
        state: {
          result: response,
          request: formData,
        },
      });
    } catch (err: any) {
      setErrorMessage(
        err.message || 'An unexpected error occurred while communicating with the prediction model.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page-wrapper">
      <section className="hero-section">
        <div className="hero-badge">
          <span className="badge-pulse"></span>
          <span>FastAPI + Scikit-Learn Pipeline</span>
        </div>
        <h1 className="hero-title">
          Accurate Indian Property <span className="gradient-text">Price Estimation</span>
        </h1>
        <p className="hero-subtitle">
          Leverage machine learning regression trained on 187,000+ real property listings to predict true market values across top Indian cities.
        </p>
      </section>

      {errorMessage && (
        <div className="alert alert-error" role="alert">
          <div className="alert-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div className="alert-body">
            <strong className="alert-heading">Prediction Request Failed</strong>
            <p className="alert-message">{errorMessage}</p>
          </div>
          <button
            type="button"
            className="alert-dismiss"
            onClick={() => setErrorMessage(null)}
            aria-label="Dismiss error"
          >
            ×
          </button>
        </div>
      )}

      <PredictionForm onSubmit={handlePredictionSubmit} isLoading={loading} />
    </div>
  );
};
