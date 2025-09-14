import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Formats cryptocurrency prices with appropriate precision
 * Handles both large prices (BTC: $115,138) and micro prices (PEPE: $0.00001054)
 * @param price - The price as a number (could be in scientific notation)
 * @param currency - The currency symbol (default: '$')
 * @returns Formatted price string
 */
export function formatCryptoPrice(price: number, currency: string = '$'): string {
  // Handle zero, null, undefined, or NaN values
  if (!price || isNaN(price) || price <= 0) {
    return `${currency}0.00`;
  }

  // Convert scientific notation to regular number if needed
  const numericPrice = Number(price);
  
  // Determine decimal places based on price magnitude
  let decimalPlaces: number;
  let useCompactNotation = false;
  
  if (numericPrice >= 1000) {
    // Large prices: use 2 decimal places with thousands separators
    decimalPlaces = 2;
    useCompactNotation = false;
  } else if (numericPrice >= 1) {
    // Medium prices ($1-$999): use 2-4 decimal places
    decimalPlaces = numericPrice >= 100 ? 2 : 4;
    useCompactNotation = false;
  } else if (numericPrice >= 0.01) {
    // Small prices ($0.01-$0.99): use 4 decimal places
    decimalPlaces = 4;
    useCompactNotation = false;
  } else if (numericPrice >= 0.0001) {
    // Very small prices: use 6 decimal places
    decimalPlaces = 6;
    useCompactNotation = false;
  } else {
    // Micro prices: determine decimal places needed to show meaningful digits
    // Find the first non-zero digit after decimal point
    const str = numericPrice.toFixed(20); // Get high precision string
    const decimalIndex = str.indexOf('.');
    let firstNonZeroIndex = -1;
    
    for (let i = decimalIndex + 1; i < str.length; i++) {
      if (str[i] !== '0') {
        firstNonZeroIndex = i;
        break;
      }
    }
    
    if (firstNonZeroIndex === -1) {
      return `${currency}0.00`;
    }
    
    // Show at least 2-3 significant digits after first non-zero
    const zerosAfterDecimal = firstNonZeroIndex - decimalIndex - 1;
    decimalPlaces = Math.min(zerosAfterDecimal + 3, 20); // Cap at 20 decimal places
    useCompactNotation = false;
  }

  try {
    const formatted = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimalPlaces,
      maximumFractionDigits: decimalPlaces,
      notation: useCompactNotation ? 'compact' : 'standard'
    }).format(numericPrice);
    
    // Replace USD symbol with custom currency if provided
    if (currency !== '$') {
      return formatted.replace('$', currency);
    }
    
    return formatted;
  } catch (error) {
    console.error('Error formatting price:', error, 'Price:', price);
    // Fallback to basic formatting
    return `${currency}${numericPrice.toFixed(decimalPlaces)}`;
  }
}
