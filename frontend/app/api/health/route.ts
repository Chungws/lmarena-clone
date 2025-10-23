/**
 * Health check endpoint for Docker healthcheck
 */
export async function GET() {
  return Response.json({
    status: "healthy",
    service: "llmbattler-frontend",
    timestamp: new Date().toISOString(),
  });
}
