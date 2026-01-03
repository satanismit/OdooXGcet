/**
 * API Base Configuration
 * Mock API base - no real backend
 */

import { sleep } from '../utils/helpers';

// Simulate API delay
export const API_DELAY = 800;

// Simulate API call with delay
export const mockApiCall = async <T>(data: T): Promise<T> => {
  await sleep(API_DELAY);
  return data;
};

// Simulate API error
export const mockApiError = async (message: string): Promise<never> => {
  await sleep(API_DELAY);
  throw new Error(message);
};
