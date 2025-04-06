import { NextResponse } from 'next/server';
import { executeMcpCommand } from '@/lib/mcp/execute';
import { type AccessibilitySnapshot } from '@/lib/types';

// This endpoint triggers the Playwright MCP server to capture an accessibility snapshot
// of the current page in the controlled browser.
export async function POST(request: Request) {
  try {
    console.log('Attempting to take browser snapshot');

    // Call the Playwright MCP server's snapshot command
    // The 'random_string' parameter is a dummy for no-parameter tools as per MCP spec
    const snapshotResult: AccessibilitySnapshot = await executeMcpCommand(
      'playwright',                     // The server name from mcp.json
      'mcp_playwright_browser_snapshot', // The MCP method for snapshot
      { random_string: 'snapshot' }      // Dummy parameter
    );

    console.log('Snapshot taken successfully.');

    // Return the snapshot data to the client
    return NextResponse.json(snapshotResult);

  } catch (error: any) {
    console.error('Error taking browser snapshot:', error);
    return NextResponse.json(
      { error: `Failed to take snapshot: ${error.message || 'Unknown error'}` },
      { status: 500 }
    );
  }
} 