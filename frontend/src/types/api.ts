export interface ApiResponse<T> {
  data?: T;
  error?: string;
  detail?: string;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
  items: T[];
}
