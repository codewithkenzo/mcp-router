import { NextResponse } from 'next/server';
import { executeMcpCommand } from '@/lib/mcp/execute';

// Define expected structures for incoming commands
interface BaseCommand {
  command: string;
  element?: string; // Human-readable description for logging/errors
}

interface ClickCommand extends BaseCommand {
  command: 'click';
  ref: string; // The reference ID from the accessibility snapshot
}

interface TypeCommand extends BaseCommand {
  command: 'type';
  ref: string;
  text: string;
  submit?: boolean;
}

// Add interfaces for other commands like hover, select, pressKey etc. as needed
// interface HoverCommand extends BaseCommand { command: 'hover'; ref: string; }
// interface SelectCommand extends BaseCommand { command: 'select'; ref: string; values: string[]; }
// interface PressKeyCommand extends BaseCommand { command: 'pressKey'; key: string; }
// interface GoBackCommand extends BaseCommand { command: 'goBack'; }
// interface GoForwardCommand extends BaseCommand { command: 'goForward'; }

type BrowserCommand = ClickCommand | TypeCommand; // | HoverCommand | SelectCommand | PressKeyCommand | GoBackCommand | GoForwardCommand;

export async function POST(request: Request) {
  try {
    // We expect a specific command structure, not free-form instructions yet
    const commandData = await request.json() as BrowserCommand;

    console.log('Received browser command:', commandData);

    let result: any;

    // TODO: Add validation for commandData fields

    switch (commandData.command) {
      case 'click':
        if (!commandData.ref) throw new Error('Missing ref for click command');
        result = await executeMcpCommand('playwright', 'mcp_playwright_browser_click', {
          ref: commandData.ref,
          element: commandData.element || 'Unnamed Element',
        });
        break;

      case 'type':
        if (!commandData.ref) throw new Error('Missing ref for type command');
        if (typeof commandData.text !== 'string') throw new Error('Missing or invalid text for type command');
        result = await executeMcpCommand('playwright', 'mcp_playwright_browser_type', {
          ref: commandData.ref,
          text: commandData.text,
          submit: commandData.submit ?? false,
          element: commandData.element || 'Unnamed Element',
        });
        break;

      // Add cases for other commands (hover, select, pressKey, goBack, goForward...)
      // case 'goBack':
      //   result = await executeMcpCommand('playwright', 'mcp_playwright_browser_go_back', { random_string: 'back' });
      //   break;
      // case 'goForward':
      //    result = await executeMcpCommand('playwright', 'mcp_playwright_browser_go_forward', { random_string: 'forward' });
      //    break;

      default:
        // Using `never` helps ensure all command types are handled
        const _exhaustiveCheck: never = commandData;
        return NextResponse.json(
          { error: `Unsupported command: ${(commandData as any).command}` },
          { status: 400 }
        );
    }

    console.log(`Command '${commandData.command}' executed successfully. Result:`, result);

    // Similar to navigate, these actions modify state but don't typically return
    // the new state directly. The frontend should request a new snapshot.
    return NextResponse.json({
      success: true,
      message: `Command '${commandData.command}' executed successfully. `,
      result: result, // Include result if the MCP command returned anything
    });

  } catch (error: any) {
    console.error('Error executing browser command:', error);
    return NextResponse.json(
      { error: `Failed to execute command: ${error.message || 'Unknown error'}` },
      { status: 500 }
    );
  }
} 