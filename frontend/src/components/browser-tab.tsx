"use client";

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { ArrowRight, Globe, Loader2, RefreshCw, ArrowLeft, /*ArrowUp, Download,*/ ExternalLink } from 'lucide-react';
import { navigateBrowser, takeBrowserSnapshot/*, clickBrowserElement, typeInBrowserElement */ } from '@/lib/mcp-browser';
import { type AccessibilitySnapshot } from '@/lib/types';

export default function BrowserTab() {
  const { toast } = useToast();
  const [url, setUrl] = useState('https://google.com'); // Default URL
  // const [browserText, setBrowserText] = useState(''); // Replaced by snapshotData
  // const [browserImage, setBrowserImage] = useState<string | null>(null); // Replaced by snapshotData
  const [snapshotData, setSnapshotData] = useState<AccessibilitySnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentLoadingAction, setCurrentLoadingAction] = useState<string | null>(null);
  const [browserHistory, setBrowserHistory] = useState<string[]>(['https://google.com']); // Start with initial URL
  const [historyIndex, setHistoryIndex] = useState(0); // Start at the initial URL
  // const [instructions, setInstructions] = useState(''); // Temporarily disable instruction input

  const handleApiError = (error: any, action: string) => {
    console.error(`Error during ${action}:`, error);
    toast({
      variant: "destructive",
      title: `${action} failed`,
      description: error.message || "An unknown error occurred.",
    });
  };

  const fetchSnapshot = async () => {
    setCurrentLoadingAction('Taking Snapshot...');
    try {
      const snapshot = await takeBrowserSnapshot();
      setSnapshotData(snapshot);
      console.log("Snapshot received:", snapshot);
    } catch (error: any) {
      handleApiError(error, 'Snapshot retrieval');
      setSnapshotData(null); // Clear snapshot on error
    } finally {
       setCurrentLoadingAction(null);
    }
  };

  const navigateTo = async (targetUrl: string, addToHistory = true) => {
    if (!targetUrl) return;

    setIsLoading(true);
    setCurrentLoadingAction('Navigating...');
    setSnapshotData(null); // Clear old snapshot

    try {
      await navigateBrowser(targetUrl);
      toast({ title: "Navigation Sent", description: `Attempting to navigate to ${targetUrl}` });

      // Update history
      if (addToHistory) {
        // If navigating forward and not already at the latest entry
        const newHistory = browserHistory.slice(0, historyIndex + 1);
        newHistory.push(targetUrl);
        setBrowserHistory(newHistory);
        setHistoryIndex(newHistory.length - 1);
      } else {
         // If navigating via back/forward, historyIndex is already set
      }

      // Update URL display immediately
      setUrl(targetUrl);

      // Fetch the snapshot after navigation request is sent
      // Add a small delay to allow page to potentially load
      await new Promise(resolve => setTimeout(resolve, 1000));
      await fetchSnapshot();

    } catch (error: any) {
      handleApiError(error, 'Navigation');
    } finally {
      setIsLoading(false);
      setCurrentLoadingAction(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Only add to history if it's a new URL typed in, not from back/forward
    const isNewUrl = historyIndex === -1 || url !== browserHistory[historyIndex];
    navigateTo(url, isNewUrl);
  };

  const handleGoBack = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      // Navigate using the URL from history, don't add it again
      navigateTo(browserHistory[newIndex], false);
    }
  };

  const handleGoForward = () => {
    if (historyIndex < browserHistory.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      // Navigate using the URL from history, don't add it again
      navigateTo(browserHistory[newIndex], false);
    }
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    setCurrentLoadingAction('Refreshing...');
    await fetchSnapshot();
    setIsLoading(false);
    setCurrentLoadingAction(null);
  };

  // Temporarily disable/simplify instruction handling
  // const handleRunInstructions = async () => {
  //   // This will be replaced with logic to parse snapshot and call click/type
  //   console.log("Instruction execution placeholder");
  //   toast({ title: "Execute (WIP)", description: "Instruction execution is under development." });
  // };

  // Remove screenshot download
  // const downloadScreenshot = () => { ... };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Web Browser (Playwright MCP)</CardTitle>
          <CardDescription>Interact with web pages using Playwright via MCP</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <div className="flex items-center space-x-2 flex-1">
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleGoBack}
                disabled={isLoading || historyIndex <= 0}
                aria-label="Go back"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleGoForward}
                disabled={isLoading || historyIndex >= browserHistory.length - 1}
                aria-label="Go forward"
              >
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleRefresh}
                disabled={isLoading}
                aria-label="Refresh"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              <div className="relative flex-1">
                <Globe className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="url"
                  placeholder="Enter URL"
                  className="pl-8"
                  value={url} // Display current URL from state
                  onChange={(e) => setUrl(e.target.value)} // Update URL state on input change
                  disabled={isLoading}
                />
              </div>
            </div>
            <Button type="submit" disabled={isLoading || !url}>
              {isLoading && currentLoadingAction === 'Navigating...' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ArrowRight className="mr-2 h-4 w-4" />}
              Go
            </Button>
          </form>

          <div className="border rounded-md p-4 min-h-[400px] relative overflow-auto bg-muted/30">
            {(isLoading || currentLoadingAction) && (
              <div className="absolute inset-0 bg-background/80 flex flex-col items-center justify-center z-10">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                {currentLoadingAction && <p className="mt-2 text-sm text-muted-foreground">{currentLoadingAction}</p>}
              </div>
            )}

            {snapshotData ? (
              <pre className="text-xs whitespace-pre-wrap break-words">
                {JSON.stringify(snapshotData, null, 2)}
              </pre>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                { !isLoading && <span>Navigate to a URL or refresh to see the page snapshot.</span> }
              </div>
            )}
          </div>

          {/* Instruction Box - Temporarily Disabled
          <Card>
            <CardHeader>
              <CardTitle>Claude Instructions</CardTitle>
              <CardDescription>Enter instructions for Claude to execute on the page.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Textarea
                placeholder="e.g., Click the 'Sign In' button, type 'example@test.com' into the email field..."
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                rows={3}
                disabled={isLoading || !snapshotData}
              />
              <Button onClick={handleRunInstructions} disabled={isLoading || !instructions || !snapshotData}>
                {isLoading && currentLoadingAction === 'Executing...' ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ArrowUp className="mr-2 h-4 w-4" />}
                Run Instructions
              </Button>
            </CardContent>
          </Card>
          */}
        </CardContent>
      </Card>
    </div>
  );
} 