import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export default function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // 1️⃣ Kalau user buka ROOT (/)
  if (pathname === "/") {
    // 2️⃣ Redirect ke /id/docs
    return NextResponse.redirect(new URL("/en/docs", request.url));
  }

  // 3️⃣ Selain itu, biarin jalan normal
  return NextResponse.next();
}
