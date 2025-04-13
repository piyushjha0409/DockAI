import dbConnect from "@/lib/dbConnect";

export async function GET() {
  try {
    await dbConnect();
    return Response.json(
      { message: "Connected to database", success: true },
      { status: 200 }
    );
  } catch (error) {
    console.error("An unexpected error occurred:", error);
    return Response.json(
      { message: "Internal server error", success: false },
      { status: 500 }
    );
  }
}
