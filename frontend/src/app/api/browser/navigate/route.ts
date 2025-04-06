import { NextResponse } from 'next/server';
import { executeMcpCommand } from '@/lib/mcp/execute'; // Import the helper

export async function POST(request: Request) {
  try {
    const { url } = await request.json();
    
    if (!url || typeof url !== 'string') { // Added type check
      return NextResponse.json(
        { error: 'URL is required and must be a string' },
        { status: 400 }
      );
    }
    
    console.log(`Attempting navigation to: ${url}`);
    
    // Call the actual Playwright MCP server
    const result = await executeMcpCommand(
      'playwright', // The name of the server in mcp.json
      'mcp_playwright_browser_navigate', // The MCP method for navigation
      { url } // Parameters for the method
    );
    
    // The navigate command typically doesn't return much, success is implied if no error
    console.log(`Navigation to ${url} command sent successfully. Result:`, result);
    
    // We might want to immediately take a snapshot after navigation
    // to return the initial page state, but let's keep this simple for now.
    return NextResponse.json({
      success: true,
      message: `Navigation to ${url} initiated successfully.`,
      // We don't get text or screenshot from navigate directly
    });
    
  } catch (error: any) { // Added type annotation
    console.error('Error in browser navigation:', error);
    return NextResponse.json(
      // Provide more specific error if possible
      { error: `Failed to navigate: ${error.message || 'Unknown error'}` },
      { status: 500 }
    );
  }
} 