import { jwtDecode } from "jwt-decode";

/**
 * Retrieves a specific cookie value by name.
 * @param {string} name - The name of the cookie.
 * @returns {string|null} - The cookie value or null if not found.
 */
const getCookie = (name: string) => {
  if (typeof document === "undefined") return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts?.pop()?.split(";")?.shift();
  return null;
};

/**
 * Decodes a JWT without verifying its signature.
 * @param {string} token - The JWT string.
 * @returns {object|null} - The decoded payload or null if invalid.
 */
export const decodeJWT = (token: string) => {
  try {
    return jwtDecode(token);
  } catch (error) {
    console.error("Failed to decode JWT:", error);
    return null;
  }
};

/**
 * Checks if the user is logged in by verifying the JWT's presence and expiration.
 * Note: This does NOT verify the JWT's signature.
 * @returns {boolean} - True if logged in and token is not expired, else false.
 */
export const isLoggedIn = () => {
  const token = getCookie("jwt");
  if (!token) {
    return false;
  }

  const decoded = decodeJWT(token);
  if (!decoded) {
    return false;
  }

  const currentTime = Date.now() / 1000; // Current time in seconds

  if (decoded.exp && decoded.exp < currentTime) {
    return false; // Token has expired
  }

  return true;
};

/**
 * Retrieves the decoded JWT payload.
 * @returns {object|null} - The decoded payload or null if invalid/not present.
 */
export const getLogged = () => {
  const token = getCookie("jwt");
  if (!token) {
    return null;
  }

  const decoded = decodeJWT(token);

  if (!decoded) {
    return null;
  }

  const currentTime = Date.now() / 1000; // Current time in seconds

  if (decoded.exp && decoded.exp < currentTime) {
    return null; // Token has expired
  }

  return decoded;
};
