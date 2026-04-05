import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

// Role cookie name
const ROLE_COOKIE = "user_role"

// Route patterns
const OWNER_ONLY_ROUTES = ["/dashboard", "/leaderboard", "/houses", "/bookings"]
const TENANT_ONLY_ROUTES = ["/tenant"]
const PUBLIC_ROUTES = ["/", "/chat", "/api"]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Get role from cookie
  const role = request.cookies.get(ROLE_COOKIE)?.value
  
  // Allow public routes
  if (PUBLIC_ROUTES.some((route) => pathname === route || pathname.startsWith(route))) {
    // Special handling for root path - redirect based on role
    if (pathname === "/") {
      if (role === "tenant") {
        return NextResponse.redirect(new URL("/tenant/houses", request.url))
      }
      if (role === "owner" || role === "both") {
        return NextResponse.redirect(new URL("/dashboard", request.url))
      }
    }
    return NextResponse.next()
  }

  // If no role cookie, allow access (client-side auth will handle it)
  if (!role) {
    return NextResponse.next()
  }

  // Check owner-only routes
  const isOwnerRoute = OWNER_ONLY_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  )
  
  if (isOwnerRoute && role === "tenant") {
    return NextResponse.redirect(new URL("/tenant/houses", request.url))
  }

  // Check tenant-only routes
  const isTenantRoute = TENANT_ONLY_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  )
  
  if (isTenantRoute && role === "owner") {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
}
