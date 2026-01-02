



import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

export interface SummaryRequest {
  url: string;
}

export interface SummaryResponse {
  success: boolean;
  title?: string;
  url?: string;
  summary?: string;
  error?: string;
}

export interface HealthResponse {
  status: string;
  bedrock_available: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SummarizerService {
  private readonly API_BASE_URL = window.location.origin;

  constructor(private http: HttpClient) {}

  /**
   * Check the health status of the API
   */
  checkHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.API_BASE_URL}/health`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Summarize content from a URL
   */
  summarizeUrl(url: string): Observable<SummaryResponse> {
    const request: SummaryRequest = { url };
    
    return this.http.post<SummaryResponse>(`${this.API_BASE_URL}/summarize`, request)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Validate URL format
   */
  isValidUrl(url: string): boolean {
    try {
      const urlObj = new URL(url);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.status === 0) {
        errorMessage = 'Unable to connect to the API server. Please ensure the server is running.';
      } else if (error.status === 404) {
        errorMessage = 'API endpoint not found. Please check the server configuration.';
      } else if (error.status >= 500) {
        errorMessage = 'Server error occurred. Please try again later.';
      } else {
        errorMessage = error.error?.error || `HTTP Error: ${error.status}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  }
}




