class ApiClient {
  private baseURL: string;
  private token: string | null = null;
  private onAuthError?: () => void;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_DURATION = 30000; // 30 seconds

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  setAuth(token: string | null, onAuthError?: () => void) {
    this.token = token;
    this.onAuthError = onAuthError;
  }

  private getAuthHeader(): Record<string, string> {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  private async handleResponse(response: Response) {
    if (!response.ok) {
      if (response.status === 401) {
        // Token is invalid, trigger auth error handler
        if (this.onAuthError) {
          this.onAuthError();
        } else {
          window.location.href = "/auth/login";
        }
        throw new Error("Authentication failed");
      }
      
      const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }
    
    return response.json();
  }

  private getCachedData(key: string) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data;
    }
    return null;
  }

  private setCachedData(key: string, data: any) {
    this.cache.set(key, { data, timestamp: Date.now() });
    // Clean old cache entries periodically
    if (this.cache.size > 100) {
      const cutoff = Date.now() - this.CACHE_DURATION;
      for (const [k, v] of this.cache.entries()) {
        if (v.timestamp < cutoff) {
          this.cache.delete(k);
        }
      }
    }
  }

  async get(endpoint: string, useCache: boolean = false) {
    // Check cache for GET requests to organizations endpoints
    if (useCache && endpoint.includes('/api/organizations')) {
      const cached = this.getCachedData(endpoint);
      if (cached) {
        return cached;
      }
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeader(),
      },
    });

    const data = await this.handleResponse(response);
    
    // Cache GET responses for organizations endpoints
    if (useCache && endpoint.includes('/api/organizations')) {
      this.setCachedData(endpoint, data);
    }

    return data;
  }

  private clearRelatedCache(endpoint: string) {
    // Clear cache for related organization endpoints when mutations occur
    if (endpoint.includes('/api/organizations')) {
      for (const key of this.cache.keys()) {
        if (key.includes('/api/organizations')) {
          this.cache.delete(key);
        }
      }
    }
  }

  async post(endpoint: string, data?: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeader(),
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    const result = await this.handleResponse(response);
    
    // Clear related cache after mutations
    this.clearRelatedCache(endpoint);
    
    return result;
  }

  async put(endpoint: string, data?: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeader(),
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    const result = await this.handleResponse(response);
    
    // Clear related cache after mutations
    this.clearRelatedCache(endpoint);
    
    return result;
  }

  async delete(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeader(),
      },
    });

    const result = await this.handleResponse(response);
    
    // Clear related cache after mutations
    this.clearRelatedCache(endpoint);
    
    return result;
  }

  async uploadFile(endpoint: string, file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "POST",
      headers: {
        ...this.getAuthHeader(),
      },
      body: formData,
    });

    return this.handleResponse(response);
  }
}

export const apiClient = new ApiClient();