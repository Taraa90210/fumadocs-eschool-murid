import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function Middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // jika akses root
  if (pathname === "/") {
    return NextResponse.redirect(new URL("/id/docs", request.url));
  }

  return NextResponse.next();
}
