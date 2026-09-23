// APNG API Client
// This file is prepared for connecting the APNG frontend
// with a backend API when the backend is available.

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Send a request to the APNG backend.
 */
export async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(
      `APNG API request failed: ${response.status} ${response.statusText}`
    );
  }

  const contentType = response.headers.get("content-type");

  if (contentType?.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

/**
 * GET request.
 */
export async function get(endpoint) {
  return apiRequest(endpoint, {
    method: "GET",
  });
}

/**
 * POST JSON data.
 */
export async function post(endpoint, data) {
  return apiRequest(endpoint, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Upload a file to the backend.
 *
 * The actual backend endpoint should be provided
 * when the backend is implemented.
 */
export async function uploadFile(endpoint, file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest(endpoint, {
    method: "POST",
    body: formData,
  });
}