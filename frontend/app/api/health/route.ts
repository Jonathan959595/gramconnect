import { NextResponse } from "next/server";
export function GET() { return NextResponse.json({ status: "ok", mode: "demo", message: "No external integrations are active." }); }
