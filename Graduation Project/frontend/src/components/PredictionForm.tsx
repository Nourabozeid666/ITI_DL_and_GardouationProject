import React, { useState } from 'react';
import {
  PredictionRequest,
  FURNISHING_OPTIONS,
  TRANSACTION_OPTIONS,
  OWNERSHIP_OPTIONS,
  FACING_OPTIONS,
} from '../types/prediction';
import locationsData from '../data/locations.json';
import { sqftToSqm } from '../utils/formatters';

interface PredictionFormProps {
  onSubmit: (data: PredictionRequest) => void;
  isLoading?: boolean;
  initialValues?: Partial<PredictionRequest>;
}

interface ValidationErrors {
  location?: string;
  carpet_area_sqft?: string;
  floor_num?: string;
  bathroom?: string;
  balcony?: string;
  furnishing?: string;
  transaction?: string;
  ownership?: string;
  facing?: string;
}

const DEFAULT_FORM: PredictionRequest = {
  location: 'Whitefield',
  carpet_area_sqft: 1200,
  floor_num: 3,
  bathroom: 2,
  balcony: 1,
  furnishing: 'Semi-Furnished',
  transaction: 'Resale',
  ownership: 'Freehold',
  facing: 'East',
};

export const PredictionForm: React.FC<PredictionFormProps> = ({
  onSubmit,
  isLoading = false,
  initialValues,
}) => {
  const [formData, setFormData] = useState<PredictionRequest>({
    ...DEFAULT_FORM,
    ...initialValues,
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validate = (data: PredictionRequest): ValidationErrors => {
    const errs: ValidationErrors = {};

    if (!data.location || data.location.trim() === '') {
      errs.location = 'Please select a valid property location.';
    }

    if (data.carpet_area_sqft === undefined || isNaN(data.carpet_area_sqft) || data.carpet_area_sqft <= 0) {
      errs.carpet_area_sqft = 'Carpet area must be greater than 0 sqft.';
    } else if (data.carpet_area_sqft < 50) {
      errs.carpet_area_sqft = 'Area seems too small (minimum 50 sqft).';
    } else if (data.carpet_area_sqft > 50000) {
      errs.carpet_area_sqft = 'Area exceeds maximum supported range (50,000 sqft).';
    }

    if (data.floor_num === undefined || isNaN(data.floor_num)) {
      errs.floor_num = 'Please enter a valid floor number (0 for Ground).';
    } else if (data.floor_num < -2 || data.floor_num > 150) {
      errs.floor_num = 'Floor must be between -2 (Basement) and 150.';
    }

    if (data.bathroom === undefined || isNaN(data.bathroom) || data.bathroom < 1) {
      errs.bathroom = 'Property must have at least 1 bathroom.';
    } else if (data.bathroom > 20) {
      errs.bathroom = 'Bathroom count cannot exceed 20.';
    }

    if (data.balcony === undefined || isNaN(data.balcony) || data.balcony < 0) {
      errs.balcony = 'Balcony count cannot be negative.';
    } else if (data.balcony > 10) {
      errs.balcony = 'Balcony count cannot exceed 10.';
    }

    if (!data.furnishing) {
      errs.furnishing = 'Please select furnishing status.';
    }

    if (!data.transaction) {
      errs.transaction = 'Please select transaction type.';
    }

    if (!data.ownership) {
      errs.ownership = 'Please select ownership status.';
    }

    if (!data.facing) {
      errs.facing = 'Please select facing direction.';
    }

    return errs;
  };

  const handleBlur = (field: keyof PredictionRequest) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors(validate(formData));
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const updatedValue = type === 'number' ? (value === '' ? ('' as any) : Number(value)) : value;

    const nextData = {
      ...formData,
      [name]: updatedValue,
    };

    setFormData(nextData);

    if (touched[name]) {
      setErrors(validate(nextData));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all as touched
    const allTouched: Record<string, boolean> = {};
    Object.keys(formData).forEach((k) => (allTouched[k] = true));
    setTouched(allTouched);

    const validationErrors = validate(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length === 0) {
      onSubmit(formData);
    }
  };

  const applyPreset = (preset: Partial<PredictionRequest>) => {
    const updated = { ...formData, ...preset };
    setFormData(updated);
    setErrors({});
  };

  return (
    <div className="card form-card">
      <div className="form-header">
        <h2 className="form-title">Enter Property Details</h2>
        <p className="form-description">
          Provide accurate property specifications to estimate the current market value.
        </p>

        <div className="presets-bar">
          <span className="preset-label">Quick Presets:</span>
          <button
            type="button"
            className="preset-btn"
            onClick={() =>
              applyPreset({
                carpet_area_sqft: 850,
                floor_num: 2,
                bathroom: 2,
                balcony: 1,
                furnishing: 'Semi-Furnished',
                transaction: 'Resale',
              })
            }
          >
            2 BHK Apt (850 sqft)
          </button>
          <button
            type="button"
            className="preset-btn"
            onClick={() =>
              applyPreset({
                carpet_area_sqft: 1800,
                floor_num: 7,
                bathroom: 3,
                balcony: 2,
                furnishing: 'Furnished',
                transaction: 'New Property',
              })
            }
          >
            3 BHK Luxury (1800 sqft)
          </button>
          <button
            type="button"
            className="preset-btn"
            onClick={() =>
              applyPreset({
                carpet_area_sqft: 500,
                floor_num: 1,
                bathroom: 1,
                balcony: 0,
                furnishing: 'Unfurnished',
                transaction: 'Resale',
              })
            }
          >
            1 BHK Studio (500 sqft)
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} noValidate className="prediction-grid-form">
        {/* Location Dropdown */}
        <div className={`form-group full-width ${errors.location && touched.location ? 'has-error' : ''}`}>
          <label htmlFor="location" className="form-label">
            Location / Neighborhood <span className="required">*</span>
          </label>
          <div className="select-wrapper">
            <select
              id="location"
              name="location"
              value={formData.location}
              onChange={handleChange}
              onBlur={() => handleBlur('location')}
              className="form-control"
              disabled={isLoading}
            >
              <option value="" disabled>Select property location</option>
              {locationsData.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>
          {errors.location && touched.location && (
            <span className="field-error-msg">{errors.location}</span>
          )}
        </div>

        {/* Carpet Area (sqft) */}
        <div className={`form-group ${errors.carpet_area_sqft && touched.carpet_area_sqft ? 'has-error' : ''}`}>
          <div className="label-with-hint">
            <label htmlFor="carpet_area_sqft" className="form-label">
              Carpet Area (sq. ft.) <span className="required">*</span>
            </label>
            {formData.carpet_area_sqft > 0 && (
              <span className="unit-conversion-hint">
                ≈ {sqftToSqm(formData.carpet_area_sqft)} m²
              </span>
            )}
          </div>
          <input
            id="carpet_area_sqft"
            name="carpet_area_sqft"
            type="number"
            min="50"
            max="50000"
            step="10"
            placeholder="e.g. 1200"
            value={formData.carpet_area_sqft || ''}
            onChange={handleChange}
            onBlur={() => handleBlur('carpet_area_sqft')}
            className="form-control"
            disabled={isLoading}
          />
          {errors.carpet_area_sqft && touched.carpet_area_sqft && (
            <span className="field-error-msg">{errors.carpet_area_sqft}</span>
          )}
        </div>

        {/* Floor Number */}
        <div className={`form-group ${errors.floor_num && touched.floor_num ? 'has-error' : ''}`}>
          <div className="label-with-hint">
            <label htmlFor="floor_num" className="form-label">
              Floor Level <span className="required">*</span>
            </label>
            <span className="field-subtext">0 = Ground Floor</span>
          </div>
          <input
            id="floor_num"
            name="floor_num"
            type="number"
            min="-2"
            max="150"
            placeholder="e.g. 3"
            value={formData.floor_num ?? ''}
            onChange={handleChange}
            onBlur={() => handleBlur('floor_num')}
            className="form-control"
            disabled={isLoading}
          />
          {errors.floor_num && touched.floor_num && (
            <span className="field-error-msg">{errors.floor_num}</span>
          )}
        </div>

        {/* Bathrooms */}
        <div className={`form-group ${errors.bathroom && touched.bathroom ? 'has-error' : ''}`}>
          <label htmlFor="bathroom" className="form-label">
            Bathrooms <span className="required">*</span>
          </label>
          <input
            id="bathroom"
            name="bathroom"
            type="number"
            min="1"
            max="20"
            placeholder="e.g. 2"
            value={formData.bathroom || ''}
            onChange={handleChange}
            onBlur={() => handleBlur('bathroom')}
            className="form-control"
            disabled={isLoading}
          />
          {errors.bathroom && touched.bathroom && (
            <span className="field-error-msg">{errors.bathroom}</span>
          )}
        </div>

        {/* Balconies */}
        <div className={`form-group ${errors.balcony && touched.balcony ? 'has-error' : ''}`}>
          <label htmlFor="balcony" className="form-label">
            Balconies <span className="required">*</span>
          </label>
          <input
            id="balcony"
            name="balcony"
            type="number"
            min="0"
            max="10"
            placeholder="e.g. 1"
            value={formData.balcony ?? ''}
            onChange={handleChange}
            onBlur={() => handleBlur('balcony')}
            className="form-control"
            disabled={isLoading}
          />
          {errors.balcony && touched.balcony && (
            <span className="field-error-msg">{errors.balcony}</span>
          )}
        </div>

        {/* Furnishing Dropdown */}
        <div className={`form-group ${errors.furnishing && touched.furnishing ? 'has-error' : ''}`}>
          <label htmlFor="furnishing" className="form-label">
            Furnishing Status <span className="required">*</span>
          </label>
          <div className="select-wrapper">
            <select
              id="furnishing"
              name="furnishing"
              value={formData.furnishing}
              onChange={handleChange}
              onBlur={() => handleBlur('furnishing')}
              className="form-control"
              disabled={isLoading}
            >
              {FURNISHING_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
          {errors.furnishing && touched.furnishing && (
            <span className="field-error-msg">{errors.furnishing}</span>
          )}
        </div>

        {/* Transaction Type Dropdown */}
        <div className={`form-group ${errors.transaction && touched.transaction ? 'has-error' : ''}`}>
          <label htmlFor="transaction" className="form-label">
            Transaction Type <span className="required">*</span>
          </label>
          <div className="select-wrapper">
            <select
              id="transaction"
              name="transaction"
              value={formData.transaction}
              onChange={handleChange}
              onBlur={() => handleBlur('transaction')}
              className="form-control"
              disabled={isLoading}
            >
              {TRANSACTION_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
          {errors.transaction && touched.transaction && (
            <span className="field-error-msg">{errors.transaction}</span>
          )}
        </div>

        {/* Ownership Type Dropdown */}
        <div className={`form-group ${errors.ownership && touched.ownership ? 'has-error' : ''}`}>
          <label htmlFor="ownership" className="form-label">
            Ownership Status <span className="required">*</span>
          </label>
          <div className="select-wrapper">
            <select
              id="ownership"
              name="ownership"
              value={formData.ownership}
              onChange={handleChange}
              onBlur={() => handleBlur('ownership')}
              className="form-control"
              disabled={isLoading}
            >
              {OWNERSHIP_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
          {errors.ownership && touched.ownership && (
            <span className="field-error-msg">{errors.ownership}</span>
          )}
        </div>

        {/* Facing Direction Dropdown */}
        <div className={`form-group ${errors.facing && touched.facing ? 'has-error' : ''}`}>
          <label htmlFor="facing" className="form-label">
            Facing Direction <span className="required">*</span>
          </label>
          <div className="select-wrapper">
            <select
              id="facing"
              name="facing"
              value={formData.facing}
              onChange={handleChange}
              onBlur={() => handleBlur('facing')}
              className="form-control"
              disabled={isLoading}
            >
              {FACING_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
          {errors.facing && touched.facing && (
            <span className="field-error-msg">{errors.facing}</span>
          )}
        </div>

        {/* Action Button */}
        <div className="form-actions full-width">
          <button
            type="submit"
            className="btn btn-primary btn-submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="btn-loading-state">
                <span className="spinner"></span>
                <span>Calculating Property Valuation...</span>
              </span>
            ) : (
              <span className="btn-content">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
                <span>Estimate Property Price</span>
              </span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
