export async function login(username, password) {
  const response = await fetch("http://localhost:8000/auth/jwt/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
  });
  const data = await response.json();
  // Store access token in localStorage or cookie
  if (data.access_token) localStorage.setItem("token", data.access_token);
  return data;
}