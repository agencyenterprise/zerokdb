import { getLogged } from "@/utils/authServer";
import { NextResponse } from "next/server";

/**
 * POST Handler to create a new request for the authenticated user to the HUB.
 */
export async function POST(req: Request) {
  try {
    const session = await getLogged();

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized: No active session found." },
        { status: 401 },
      );
    }

    const data = await req.json();

    const ownerWallet = (session as any).address;

    const backendUrl =
      process.env.HUB_URL ||
      "https://g1cqd9cf69e1b0tj8fd7o85mdg.ingress.akashprovid.com";
    const backendAuthToken = process.env.HUB_AUTH_TOKEN || "";

    const ai_model_inputs = data.semantic?.length
      ? {
          type: "TEXT",
          value: { text: data.semantic, table_name: data?.table },
        }
      : {
          type: "SQL",
          value: data?.sql?.split(/\s+/)?.join(" ")?.trim(),
        };

    const response = await fetch(`${backendUrl}/proof_requests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": backendAuthToken,
      },
      body: JSON.stringify({
        chain: "aptos_testnet",
        owner_wallet: ownerWallet,
        name: data.semantic?.length
          ? ai_model_inputs?.value?.text?.substring(0, 30)
          : ai_model_inputs?.value?.substring(0, 30),
        description: data.semantic?.length
          ? ai_model_inputs?.value?.text
          : ai_model_inputs?.value,
        ai_model_name: "zerokdb",
        ai_model_inputs: JSON.stringify(ai_model_inputs),
      }),
    });

    if (!response.ok) {
      const message = "Failed to execute request";
      console.log(message, response);
      return NextResponse.json(
        {
          error: message,
        },
        { status: 500 },
      );
    }

    const proofRequest = await response.json();

    return NextResponse.json(proofRequest, { status: 200 });
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

/**
 * GET Handler to retrieve all proof requests for the authenticated user.
 */
export async function GET(req: Request) {
  try {
    const session = await getLogged();

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized: No active session found." },
        { status: 401 },
      );
    }

    const ownerWallet = (session as any).address;

    const backendUrl =
      process.env.HUB_URL ||
      "https://g1cqd9cf69e1b0tj8fd7o85mdg.ingress.akashprovid.com";
    const backendAuthToken = process.env.HUB_AUTH_TOKEN || "";

    const apiUrl = `${backendUrl}/proof_requests/${encodeURIComponent(
      ownerWallet,
    )}`;

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
          error: "Failed to retrieve requests.",
          details: errorData,
        },
        { status: response.status },
      );
    }

    // Parse the response JSON
    const data = await response.json();

    // Return the list of proof requests as a JSON response with a 200 OK status
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error("Error in GET /api/hub/requests:", error);
    return NextResponse.json(
      {
        error: "Internal Server Error",
        message: error.message || "An unexpected error occurred.",
      },
      { status: 500 },
    );
  }
}
