/**
 * Currency formatting utility for consistent EUR currency display
 */

export function formatEUR(value: number): string {
  return `€${value.toFixed(2)}`;
}
