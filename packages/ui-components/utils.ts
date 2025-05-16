import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Funkcja łącząca klasy CSS, która dodatkowo usuwa konflikty klas Tailwind
 * 
 * @param inputs Lista klas CSS do połączenia
 * @returns Połączone i oczyszczone klasy CSS
 * 
 * @example
 * cn('text-red-500', 'bg-blue-500', { 'hidden': isHidden })
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
} 