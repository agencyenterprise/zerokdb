import { NextRequest, NextResponse } from "next/server";
import jwt from "jsonwebtoken";
import { cookies } from "next/headers";
import { verifySignature } from "@/utils/auth";

const BACKEND_AUTH_TOKEN =
  process.env.BACKEND_AUTH_TOKEN || "your_BACKEND_AUTH_TOKEN_key";

export async function POST(request: NextRequest) {
  const signature = await request.json();

  const cookieStore = cookies();
  const storedNonce = cookieStore.get("auth_nonce")?.value;

  if (!storedNonce || !signature.nonce) {
    console.error("Nonce not found or expired");
    return NextResponse.json(
      { error: "Nonce not found or expired" },
      { status: 400 },
    );
  }

  const signatureNonce = JSON.parse(signature.nonce);

  if (storedNonce !== signatureNonce.nonce) {
    console.error("Nonce mismatch");
    return NextResponse.json({ error: "Nonce mismatch" }, { status: 400 });
  }

  const isValid = verifySignature(signature);

  if (isValid) {
    const token = jwt.sign({ address: signature.address }, BACKEND_AUTH_TOKEN, {
      expiresIn: "1h",
    });

    const response = NextResponse.json({ success: true });

    // Set JWT cookie and delete nonce cookie
    response.cookies.set("jwt", token, {
      httpOnly: true,
      path: "/",
      maxAge: 604800, // 1 week
      sameSite: "strict",
      secure: process.env.NODE_ENV === "production",
    });

    response.cookies.delete("auth_nonce");

    return response;
  } else {
    console.error("Invalid signature");
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }
}
