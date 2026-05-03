const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  let data = null;

  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.error ||
      data?.message ||
      "Something went wrong. Please try again.";
    throw new Error(message);
  }

  return data;
}

export function registerUser(payload) {
  return request("/api/users/register/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload) {
  const identifier = (payload.email || payload.username || "").trim();
  return request("/api/login/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: identifier,
      password: payload.password,
    }),
  });
}

export function fetchClaims(token) {
  return request("/api/claims/uploads/", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function uploadClaim(token, file, referenceFile, mediaType) {
  const formData = new FormData();
  formData.append("media", file);
  formData.append("media_type", mediaType);
  if (referenceFile) {
    formData.append("reference_media", referenceFile);
  }

  return request("/api/claims/uploads/", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
}
