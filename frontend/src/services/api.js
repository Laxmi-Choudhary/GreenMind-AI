// frontend/src/services/api.js

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const getAuthToken = () => {
  return localStorage.getItem("greenmind_token");
};

const removeAuthToken = () => {
  localStorage.removeItem("greenmind_token");
};

const request = async (endpoint, options = {}) => {
  const token = getAuthToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: "include", // send HttpOnly cookies
    });

    // Handle Unauthorized responses
    if (response.status === 401) {
      removeAuthToken();

      // Redirect to login if desired
      // window.location.href = "/login";

      throw new Error("Session expired. Please login again.");
    }

    if (!response.ok) {
      let errorMessage = "An unexpected error occurred.";

      try {
        const errorData = await response.json();
        errorMessage =
          errorData.detail ||
          errorData.message ||
          errorMessage;
      } catch {
        // Ignore JSON parsing errors
      }

      const error = new Error(errorMessage);
      error.status = response.status;

      throw error;
    }

    // No content response
    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get("content-type");

    if (
      contentType &&
      contentType.includes("application/json")
    ) {
      return await response.json();
    }

    return await response.text();

  } catch (error) {
    console.error("API Error:", error);

    if (!navigator.onLine) {
      throw new Error(
        "No internet connection. Please check your network."
      );
    }

    throw error;
  }
};

export const api = {
  get: (endpoint, options = {}) =>
    request(endpoint, {
      method: "GET",
      ...options,
    }),

  post: (endpoint, body = {}, options = {}) =>
    request(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
      ...options,
    }),

  put: (endpoint, body = {}, options = {}) =>
    request(endpoint, {
      method: "PUT",
      body: JSON.stringify(body),
      ...options,
    }),

  patch: (endpoint, body = {}, options = {}) =>
    request(endpoint, {
      method: "PATCH",
      body: JSON.stringify(body),
      ...options,
    }),

  delete: (endpoint, options = {}) =>
    request(endpoint, {
      method: "DELETE",
      ...options,
    }),
};

export default api;