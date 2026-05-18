import API_BASE_URL from "../config";

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  if (config.body && typeof config.body === "object" && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  if (config.body instanceof FormData) {
    delete headers["Content-Type"];
    config.headers = headers;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text().catch(() => null);
    }
    throw new ApiError(
      errorData?.detail || `HTTP ${response.status}`,
      response.status,
      errorData,
    );
  }

  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    return response.json();
  }
  return response;
}

export const api = {
  get: (endpoint, options) => request(endpoint, { ...options, method: "GET" }),
  post: (endpoint, body, options) =>
    request(endpoint, { ...options, method: "POST", body }),
  put: (endpoint, body, options) =>
    request(endpoint, { ...options, method: "PUT", body }),
  delete: (endpoint, options) =>
    request(endpoint, { ...options, method: "DELETE" }),
};

export { ApiError };
