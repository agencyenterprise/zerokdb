import { getLogged } from "@/utils/authServer";
import { NextResponse } from "next/server";

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

    const backendUrl = process.env.HUB_URL || "http://localhost:8000";
    const backendAuthToken = process.env.HUB_AUTH_TOKEN || "";

    const ai_model_inputs = data.semantic?.length
      ? { type: "TEXT", value: data.semantic }
      : { type: "SQL", value: data.sql };

    const response = await fetch(`${backendUrl}/proof_requests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": backendAuthToken,
      },
      body: JSON.stringify({
        chain: "aptos_testnet",
        owner_wallet: ownerWallet,
        name: ai_model_inputs.value.substring(0, 30),
        description: ai_model_inputs.value,
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
