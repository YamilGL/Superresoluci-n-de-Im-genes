import { Component, ViewChild } from '@angular/core';
import { FileUpload } from 'primeng/fileupload';
import { ImageProcessingService, ProcessImageResponse } from './app.service';
import { CommonModule } from '@angular/common';

interface GalleriaImage {
  itemImageSrc: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  @ViewChild('fileUpload') fileUpload!: FileUpload;

  images: GalleriaImage[] = [];
  QR: any[] = [
    {
      itemImageSrc: '../assets/QR.png',
      thumbnailImageSrc: '../assets/QR.png', // Si llegas a usar miniaturas
      alt: 'QR Code',
      title: 'QR Code'
    }
  ];
  hasUploadedImage: boolean = false;
  uploadedFile: File | null = null;
  processingResult: ProcessImageResponse | null = null;
  isProcessing: boolean = false;
  isResult: boolean = false;

  constructor(private imageProcessingService: ImageProcessingService) {}

  onUpload(event: any) {
    const file = event.files[0];
    if (file) {
      this.uploadedFile = file;
      const reader = new FileReader();
      reader.onload = (e: any) => {
        const newImage: GalleriaImage = {
          itemImageSrc: e.target.result
        };
        this.images = [newImage];
        this.hasUploadedImage = true;
      };
      reader.readAsDataURL(file);
    }
  }

  onCancel() {
    this.images = [];
    this.hasUploadedImage = false;
    this.uploadedFile = null;
    this.processingResult = null;
    this.isProcessing = false;
    this.isResult = false
    if (this.fileUpload) {
      this.fileUpload.clear();
    }
  }

  onProcess(scale: '2' | '3' | '4') {
    if (!this.uploadedFile) {
      console.error('No file uploaded');
      return;
    }

    this.isProcessing = true;
    this.isResult = true;

    this.imageProcessingService.processImage(this.uploadedFile, scale).subscribe(
      (response) => {
        this.processingResult = response;
        this.isProcessing = false;
      },
      (error) => {
        console.error(`Error in process x${scale}:`, error);
        this.isProcessing = false;
      }
    );
  }

  getImageUrl(path: string): string {
    return this.imageProcessingService.getImageUrl(path);
  }
}
