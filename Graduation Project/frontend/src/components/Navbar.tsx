import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { checkBackendHealth } from '../api/predictionClient';

export const Navbar: React.FC = () => {
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);
  const location = useLocation();

  useEffect(() => {
    let isMounted = true;
    checkBackendHealth().then((res) => {
      if (isMounted) {
        setIsBackendOnline(res.status === 'healthy' || res.status === 'ok');
      }
    });
    return () => {
      isMounted = false;
    };
  }, [location.pathname]);

  return (
    <header className="navbar-container">
      <div className="navbar-content">
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </div>
          <div className="brand-text">
            <span className="brand-title">RealEstate<span className="accent">AI</span></span>
            <span className="brand-subtitle">House Price Estimator</span>
          </div>
        </Link>

        <div className="navbar-actions">
          <div className={`status-indicator ${isBackendOnline === null ? 'status-checking' : isBackendOnline ? 'status-online' : 'status-offline'}`}>
            <span className="status-dot"></span>
            <span className="status-label">
              {isBackendOnline === null ? 'API: Connecting...' : isBackendOnline ? 'API: Ready' : 'API: Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
