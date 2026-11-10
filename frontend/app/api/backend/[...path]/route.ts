import { NextRequest } from "next/server";

const methods = ["GET", "POST", "PATCH"] as const;

async function forward(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const baseUrl = (process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");
  if (!baseUrl) return Response.json({ detail: "Backend service is not configured." }, { status: 503 });
  const { path } = await context.params;
  const target = `${baseUrl}/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  const authorization = request.headers.get("authorization");
  if (contentType) headers.set("content-type", contentType);
  if (authorization) headers.set("authorization", authorization);
  const response = await fetch(target, { method: request.method, headers, body: request.method === "GET" ? undefined : await request.text(), cache: "no-store" });
  return new Response(await response.arrayBuffer(), { status: response.status, headers: { "content-type": response.headers.get("content-type") || "application/json" } });
}

export const GET = forward;
export const POST = forward;
export const PATCH = forward;
