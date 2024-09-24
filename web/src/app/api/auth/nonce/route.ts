import { NextRequest, NextResponse } from "next/server";
import { v4 as uuidv4 } from "uuid";

export async function GET(request: NextRequest) {
  const nonceValue = uuidv4();

  // Set the nonce in an HttpOnly cookie
  const response = NextResponse.json({ nonce: nonceValue });

  response.cookies.set("auth_nonce", nonceValue, {
    httpOnly: true,
    path: "/",
    maxAge: 300, // 5 minutes
    sameSite: "strict",
    secure: process.env.NODE_ENV === "production",
  });

  return response;
}
