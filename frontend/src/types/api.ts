export interface ApiErrorResponse {
  success: boolean;
  status_code: number;
  error: {
    message: string;
    code: string;
    details?: Array<{ field: string; message: string }>;
  };
}
