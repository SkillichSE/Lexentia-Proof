import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

export async function middleware(request: NextRequest) {
  // Rewrite root path to legacy index without changing URL
  if (request.nextUrl.pathname === "/") {
    const rewriteUrl = request.nextUrl.clone();
    rewriteUrl.pathname = "/legacy/index";
    return NextResponse.rewrite(rewriteUrl);
  }

  let response = NextResponse.next({ request });
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || "",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "",
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value;
        },
        set(name: string, value: string, options: Record<string, unknown>) {
          request.cookies.set({ name, value, ...(options || {}) });
          response = NextResponse.next({ request });
          response.cookies.set({ name, value, ...(options || {}) });
        },
        remove(name: string, options: Record<string, unknown>) {
          request.cookies.set({ name, value: "", ...(options || {}) });
          response = NextResponse.next({ request });
          response.cookies.set({ name, value: "", ...(options || {}), maxAge: 0 });
        }
      }
    }
  );

  const {
    data: { user }
  } = await supabase.auth.getUser();

  if (!user) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/auth/login";
    redirectUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(redirectUrl);
  }

  return response;
}

export const config = {
  matcher: ["/", "/author/:path*", "/dashboard/:path*"]
};
