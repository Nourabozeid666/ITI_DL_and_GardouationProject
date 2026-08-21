import React from 'react';
import { Link } from 'react-router-dom';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="card not-found-card">
      <div className="not-found-badge">404</div>
      <h1 className="not-found-title">Page Not Found</h1>
      <p className="not-found-text">
        The page or resource you are looking for does not exist or has been moved.
      </p>
      <Link to="/" className="btn btn-primary">
        Return to Home
      </Link>
    </div>
  );
};
