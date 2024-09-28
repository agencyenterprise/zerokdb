import { getLogged } from "@/utils/authServer";
import { NextResponse } from "next/server";

/**
 * GET Handler to retrieve a specific proof request by ID for the authenticated user.
 */
export async function GET(
  req: Request,
  { params }: { params: { id: string } },
) {
  try {
    const proofRequestId = params.id;

    if (!proofRequestId) {
      return NextResponse.json(
        { error: "Proof request ID is required." },
        { status: 400 },
      );
    }

    // Retrieve the current user's session
    const session = await getLogged();

    // If no session is found, return a 401 Unauthorized response
    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized: No active session found." },
        { status: 401 },
      );
    }

    // Extract the user's wallet address from the session
    const ownerWallet = (session as any).address;

    // Retrieve backend URL and authentication token from environment variables
    const backendUrl = process.env.HUB_URL || "http://localhost:8000";
    const backendAuthToken = process.env.HUB_AUTH_TOKEN || "";

    // Construct the backend API URL using owner_wallet and proofRequestId
    const apiUrl = `${backendUrl}/${encodeURIComponent(
      ownerWallet,
    )}/${encodeURIComponent(proofRequestId)}`;

    // Make a GET request to the backend API to fetch the proof request
    const response = await fetch(apiUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": backendAuthToken,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        {
          error: "Failed to retrieve request.",
          details: errorData,
        },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error("Error in GET /api/hub/request/[id]:", error);
    return NextResponse.json(
      {
        error: "Internal Server Error",
        message: error.message || "An unexpected error occurred.",
      },
      { status: 500 },
    );
  }
}
