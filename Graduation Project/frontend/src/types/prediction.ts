export interface PredictionRequest {
  location: string;
  carpet_area_sqft: number;
  floor_num: number;
  bathroom: number;
  balcony: number;
  furnishing: 'Furnished' | 'Semi-Furnished' | 'Unfurnished' | string;
  transaction: 'New Property' | 'Resale' | string;
  ownership: 'Freehold' | 'Leasehold' | 'Co-operative Society' | 'Power of Attorney' | string;
  facing: 'East' | 'North' | 'South' | 'West' | 'North-East' | 'North-West' | 'South-East' | 'South-West' | 'Unknown' | string;
}

export interface PredictionResponse {
  predicted_price: number;
  currency?: string;
  formatted_price?: string;
  features_used?: PredictionRequest;
}

export interface ApiError {
  message: string;
  detail?: string | Array<{ loc?: string[]; msg?: string; type?: string }>;
}

export const FURNISHING_OPTIONS = [
  'Furnished',
  'Semi-Furnished',
  'Unfurnished',
] as const;

export const TRANSACTION_OPTIONS = [
  'New Property',
  'Resale',
] as const;

export const OWNERSHIP_OPTIONS = [
  'Freehold',
  'Leasehold',
  'Co-operative Society',
  'Power of Attorney',
] as const;

export const FACING_OPTIONS = [
  'East',
  'North',
  'West',
  'South',
  'North-East',
  'North-West',
  'South-East',
  'South-West',
  'Unknown',
] as const;
