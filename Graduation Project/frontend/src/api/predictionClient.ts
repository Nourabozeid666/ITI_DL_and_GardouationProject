import { PredictionRequest, PredictionResponse } from '../types/prediction';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Clean URL joiner to avoid double slashes.
 */
function buildUrl(path: string): string {
  const cleanBase = BASE_URL.replace(/\/+$/, '');
  const cleanPath = path.replace(/^\/+/, '');
  return `${cleanBase}/${cleanPath}`;
}

/**
 * Parses API error details from FastAPI responses.
 */
function extractErrorMessage(status: number, data: any): string {
  if (data && typeof data === 'object') {
    if (typeof data.detail === 'string') {
      return data.detail;
    }
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      const first = data.detail[0];
      const loc = Array.isArray(first.loc) ? first.loc.slice(1).join('.') : '';
      return `${loc ? `[${loc}] ` : ''}${first.msg || 'Invalid field format'}`;
    }
    if (data.message) {
      return data.message;
    }
  }
  return `Server responded with error (HTTP ${status})`;
}

/**
 * Sends property features to the backend for price estimation.
 */
export async function getPricePrediction(payload: PredictionRequest): Promise<PredictionResponse> {
  const endpoints = ['predict', 'api/v1/predict', 'predict/'];
  let lastError: Error | null = null;

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(buildUrl(endpoint), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const result = await response.json();
        return {
          predicted_price: result.predicted_price,
          currency: result.currency || 'INR',
          formatted_price: result.formatted_price,
          features_used: result.features_used || payload,
        };
      }

      const errorBody = await response.json().catch(() => null);
      // If we got a 422 or 400 from the backend, do not retry other routes - throw immediately
      if (response.status === 422 || response.status === 400) {
        throw new Error(extractErrorMessage(response.status, errorBody));
      }

      if (response.status !== 404) {
        throw new Error(extractErrorMessage(response.status, errorBody));
      }

      // If 404, loop to try the next endpoint variation
      lastError = new Error(`Endpoint /${endpoint} not found (HTTP 404).`);
    } catch (err: any) {
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        throw new Error(
          `Unable to connect to the backend server at ${BASE_URL}. Please ensure the FastAPI server is running.`
        );
      }
      if (err.message && !err.message.includes('404')) {
        throw err;
      }
      lastError = err;
    }
  }

  throw lastError || new Error('Failed to reach prediction service.');
}

/**
 * Health check endpoint for the backend API.
 */
export async function checkBackendHealth(): Promise<{ status: string; service?: string }> {
  try {
    const response = await fetch(buildUrl('health'), {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Health check failed with status ${response.status}`);
    }
    return await response.json();
  } catch (err: any) {
    return { status: 'offline' };
  }
}
