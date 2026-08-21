/**
 * Formats a monetary value into Indian Rupee denomination string (₹ ... Lac / ₹ ... Cr).
 *
 * @param amount - Price numeric value (either in Lakhs or raw Rupees)
 * @param isRawRupees - Set to true if the number is in raw INR, false if in Lakhs
 */
export function formatIndianPrice(amount: number, isRawRupees = false): string {
  if (isNaN(amount) || amount === null || amount === undefined) {
    return '₹ 0';
  }

  // Convert to raw rupees for consistent scale calculation
  const rawINR = isRawRupees ? amount : (amount > 10000 ? amount : amount * 100000);

  if (rawINR >= 10000000) {
    const cr = rawINR / 10000000;
    return `₹ ${cr.toFixed(2)} Cr`;
  } else if (rawINR >= 100000) {
    const lac = rawINR / 100000;
    return `₹ ${lac.toFixed(2)} Lac`;
  } else {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(rawINR);
  }
}

/**
 * Converts square feet to square meters.
 */
export function sqftToSqm(sqft: number): number {
  return parseFloat((sqft / 10.764).toFixed(2));
}

/**
 * Calculates estimated price per square foot.
 */
export function calculatePricePerSqft(priceInRupees: number, sqft: number): string {
  if (!sqft || sqft <= 0) return '—';
  const pricePerSqft = priceInRupees / sqft;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(pricePerSqft);
}
