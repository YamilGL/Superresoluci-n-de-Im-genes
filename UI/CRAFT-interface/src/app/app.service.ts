import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ProcessImageResponse {
  message: string;
  inputImage: string;
  resultImage: string;
  commandOutput: string;
}

@Injectable({
  providedIn: 'root'
})
export class ImageProcessingService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  processImage(file: File, scale: '2' | '3' | '4'): Observable<ProcessImageResponse> {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('scale', `x${scale}`);

    return this.http.post<ProcessImageResponse>(`${this.apiUrl}/process_image`, formData);
  }

  getImageUrl(path: string): string {
    const [prefix, scale, filename] = path.split('/');
    if (prefix === 'results') {
      return `http://localhost:5000/results/${scale}/${filename}`;
    }
    return '';
  }
}
