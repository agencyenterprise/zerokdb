import { cookies } from "next/headers";
import jwt from "jsonwebtoken";
import nacl from "tweetnacl";
import { sha3_256 } from "js-sha3";

const BACKEND_AUTH_TOKEN =
  process.env.BACKEND_AUTH_TOKEN || "your_BACKEND_AUTH_TOKEN_key";

// Utility function to normalize addresses
function normalizeAddress(address: string): string {
  return address.replace(/^0x/, "").toLowerCase();
}

// Function to compute the Aptos address from the public key
export function getAddressFromPublicKey(publicKeyHex: string): string {
  const publicKeyHexClean = publicKeyHex.replace(/^0x/, "");
  const publicKeyBytes = Uint8Array.from(Buffer.from(publicKeyHexClean, "hex"));

  // Append a 0x00 byte to the public key bytes
  const publicKeyWithZeroByte = new Uint8Array(publicKeyBytes.length + 1);
  publicKeyWithZeroByte.set(publicKeyBytes);
  publicKeyWithZeroByte[publicKeyBytes.length] = 0x00;

  // Compute the SHA3-256 hash of the public key with zero byte appended
  const hashArrayBuffer = sha3_256.arrayBuffer(publicKeyWithZeroByte);
  const hashBytes = new Uint8Array(hashArrayBuffer);

  // Convert the hash bytes to a hex string
  const addressHex = Buffer.from(hashBytes).toString("hex");
  return addressHex;
}

// Function to verify the signature and address
// Function to verify the signature and address
export function verifySignature(signatureObj: any): boolean {
  try {
    const { address, fullMessage, publicKey, signature } = signatureObj;

    if (!publicKey) {
      console.error("Public key is missing");
      return false;
    }

    // Compute address from publicKey
    const computedAddress = getAddressFromPublicKey(publicKey);

    // Normalize addresses
    const providedAddress = normalizeAddress(address || "");
    const computedAddressNormalized = normalizeAddress(computedAddress);

    if (providedAddress !== computedAddressNormalized) {
      console.error("Address does not match public key");
      return false;
    }

    // Convert publicKey to bytes
    const publicKeyHex = publicKey.replace(/^0x/, "");
    const publicKeyBytes = Uint8Array.from(Buffer.from(publicKeyHex, "hex"));

    // Check if signature is a string and convert it to bytes if necessary
    let signatureBytes;
    if (typeof signature === "string") {
      // Convert the signature hex string to bytes
      const signatureHex = signature.replace(/^0x/, "");
      signatureBytes = Uint8Array.from(Buffer.from(signatureHex, "hex"));
    } else {
      console.error("Invalid signature format");
      return false;
    }

    // Ensure signatureBytes length is 64 bytes
    if (signatureBytes.length !== 64) {
      console.error(
        `Invalid signature length: ${signatureBytes.length}. Expected 64 bytes.`,
      );
      return false;
    }

    // Encode the message
    const messageBytes = new TextEncoder().encode(fullMessage);

    // Verify the signature
    const isValid = nacl.sign.detached.verify(
      messageBytes,
      signatureBytes,
      publicKeyBytes,
    );

    return isValid;
  } catch (error) {
    console.error("Error verifying signature:", error);
    return false;
  }
}

// Check if the user is logged in by verifying the JWT
export async function isLoggedIn() {
  const jwtCookie = cookies().get("jwt");
  if (!jwtCookie?.value) {
    return false;
  }

  try {
    jwt.verify(jwtCookie.value, BACKEND_AUTH_TOKEN);
    return true;
  } catch (error) {
    console.error("Invalid JWT:", error);
    return false;
  }
}

// Get the logged-in user's information from the JWT
export async function getLogged() {
  const jwtCookie = cookies().get("jwt");
  if (!jwtCookie?.value) {
    return null;
  }

  try {
    const decoded = jwt.verify(jwtCookie.value, BACKEND_AUTH_TOKEN);
    return decoded; // Contains the address and other JWT claims
  } catch (error) {
    console.error("Invalid JWT:", error);
    return null;
  }
}

// Log out the user by clearing the JWT cookie
export async function logout() {
  cookies().set({
    name: "jwt",
    value: "",
    httpOnly: false,
    path: "/",
    expires: new Date(0),
  });
}
