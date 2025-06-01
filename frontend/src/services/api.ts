class ApiClient {
  private baseURL: string;
  private token: string | null = null;
  private onAuthError?: () => void;

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

  async get(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeader(),
      },
    });

    return this.handleResponse(response);
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

    return this.handleResponse(response);
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

    return this.handleResponse(response);
  }

  async delete(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeader(),
      },
    });

    return this.handleResponse(response);
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