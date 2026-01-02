




import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SummarizerService, SummaryResponse, HealthResponse } from './summarizer.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'AI Web Content Summarizer';
  
  summaryForm: FormGroup;
  isLoading = false;
  summaryResult: SummaryResponse | null = null;
  errorMessage: string | null = null;
  healthStatus: HealthResponse | null = null;
  
  // Sample URLs for testing
  sampleUrls = [
    {
      name: 'Federal Reserve Research Paper',
      url: 'https://www.federalreserve.gov/econres/feds/the-effect-of-liquidity-constraints-on-labor-supply-evidence-from-interest-rate-ceilings.htm'
    },
    {
      name: 'Wikipedia - Artificial Intelligence',
      url: 'https://en.wikipedia.org/wiki/Artificial_intelligence'
    },
    {
      name: 'Wikipedia - Machine Learning',
      url: 'https://en.wikipedia.org/wiki/Machine_learning'
    },
    {
      name: 'Wikipedia - Python Programming',
      url: 'https://en.wikipedia.org/wiki/Python_(programming_language)'
    }
  ];

  constructor(
    private fb: FormBuilder,
    private summarizerService: SummarizerService
  ) {
    this.summaryForm = this.fb.group({
      url: ['', [Validators.required, this.urlValidator.bind(this)]]
    });
  }

  ngOnInit(): void {
    this.checkApiHealth();
  }

  /**
   * Custom URL validator
   */
  urlValidator(control: any) {
    if (!control.value) {
      return null;
    }
    
    const isValid = this.summarizerService.isValidUrl(control.value);
    return isValid ? null : { invalidUrl: true };
  }

  /**
   * Check API health status
   */
  checkApiHealth(): void {
    this.summarizerService.checkHealth().subscribe({
      next: (health) => {
        this.healthStatus = health;
      },
      error: (error) => {
        console.error('Health check failed:', error);
        this.healthStatus = {
          status: 'error',
          bedrock_available: false
        };
      }
    });
  }

  /**
   * Handle form submission
   */
  onSubmit(): void {
    if (this.summaryForm.valid && !this.isLoading) {
      const url = this.summaryForm.get('url')?.value;
      this.summarizeUrl(url);
    }
  }

  /**
   * Summarize the provided URL
   */
  summarizeUrl(url: string): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.summaryResult = null;

    this.summarizerService.summarizeUrl(url).subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response.success) {
          this.summaryResult = response;
        } else {
          this.errorMessage = response.error || 'Failed to generate summary';
        }
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.message;
      }
    });
  }

  /**
   * Use a sample URL
   */
  useSampleUrl(url: string): void {
    this.summaryForm.patchValue({ url });
    this.clearResults();
  }

  /**
   * Clear form and results
   */
  clearForm(): void {
    this.summaryForm.reset();
    this.clearResults();
  }

  /**
   * Clear results only
   */
  clearResults(): void {
    this.summaryResult = null;
    this.errorMessage = null;
  }

  /**
   * Get form control for template access
   */
  get urlControl() {
    return this.summaryForm.get('url');
  }

  /**
   * Check if URL field has errors
   */
  get hasUrlError(): boolean {
    const control = this.urlControl;
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  /**
   * Get URL error message
   */
  get urlErrorMessage(): string {
    const control = this.urlControl;
    if (control?.errors) {
      if (control.errors['required']) {
        return 'URL is required';
      }
      if (control.errors['invalidUrl']) {
        return 'Please enter a valid URL (must start with http:// or https://)';
      }
    }
    return '';
  }

  /**
   * Format summary text with line breaks
   */
  formatSummary(text: string): string {
    if (!text) return '';
    return text.split('\n').join('<br>');
  }
}





