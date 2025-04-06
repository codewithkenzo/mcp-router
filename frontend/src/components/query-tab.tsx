"use client";

import { useState, useRef, useEffect } from "react";
// import { useQuery, useMutation } from "react-query"; // Remove react-query for now
import axios from "axios"; // Keep axios for direct API calls
import { Send, /*MessageSquare,*/ Sparkles, Loader2, /*InfoIcon*/ } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
// Remove unused imports: Select, Checkbox, Label, ScrollArea, Tooltip, mock data
import { Card, CardContent, CardDescription, /*CardFooter,*/ CardHeader, CardTitle } from "@/components/ui/card";
import { useTasks } from "@/context/TaskContext"; // Import useTasks hook

// Define types for the new workflow
interface AnalysisResult {
  goal: string;
  requiredTools: string[];
  // Add other fields as needed based on actual analysis output
}

export default function QueryTab() {
  const { toast } = useToast();
  const { addTaskId } = useTasks(); // Get addTaskId function from context
  const [prompt, setPrompt] = useState("");
  // const [selectedModel, setSelectedModel] = useState<string>(""); // Removed
  // const [selectedServers, setSelectedServers] = useState<string[]>([]); // Removed
  // const [result, setResult] = useState<QueryResponse | null>(null); // Removed old result structure

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRunningTask, setIsRunningTask] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [latestTaskId, setLatestTaskId] = useState<string | null>(null); // Renamed from taskId for clarity

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto resize textarea as content grows
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [prompt]);

  // Remove model and server fetching logic (useQuery hooks)

  // Handle prompt submission to Upsonic workflow
  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      toast({
        title: "Empty Prompt",
        description: "Please enter a prompt to start a task.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setLatestTaskId(null); // Clear previous task ID
    setIsRunningTask(false);

    let currentAnalysisResult: AnalysisResult | null = null;

    try {
      // Step 1: Analyze the prompt
      toast({ title: "Analyzing Prompt...", description: "Determining required tools..." });
      const analyzeResponse = await axios.post("/api/upsonic/analyze", { prompt });
      currentAnalysisResult = analyzeResponse.data;
      setAnalysisResult(currentAnalysisResult);
      setIsAnalyzing(false);
      toast({ title: "Analysis Complete", description: `Required tools: ${currentAnalysisResult?.requiredTools.join(', ') || 'None identified'}` });

      if (!currentAnalysisResult || !currentAnalysisResult.requiredTools || currentAnalysisResult.requiredTools.length === 0) {
         toast({ title: "No Tools Identified", description: "Could not determine required tools for this prompt.", variant: "destructive" });
         // Optionally allow proceeding without tools if Upsonic/LLM can handle it
         // For now, we stop if no tools are found by the basic analyzer.
         return;
      }

      // Step 2: Run the task with the analysis result
      setIsRunningTask(true);
      toast({ title: "Starting Task...", description: "Sending task to Upsonic service..." });
      const runResponse = await axios.post("/api/upsonic/run", currentAnalysisResult);
      const returnedTaskId = runResponse.data.taskId;

      if (returnedTaskId) {
        setLatestTaskId(returnedTaskId);
        addTaskId(returnedTaskId); // Add the ID to the shared context
        toast({ title: "Task Started!", description: `Task ID: ${returnedTaskId}. Monitor progress in the Tasks tab.` });
        setPrompt(""); // Clear prompt on successful start
      } else {
        throw new Error("Backend did not return a task ID.");
      }
      setIsRunningTask(false);

    } catch (error: any) {
      console.error("Error during Upsonic task submission:", error);
      const action = isAnalyzing ? "Analysis" : "Task Start";
      toast({
        title: `${action} Failed`,
        description: error.response?.data?.error || error.message || "An unknown error occurred.",
        variant: "destructive",
      });
      // Reset states on error
      setIsAnalyzing(false);
      setIsRunningTask(false);
      // Keep analysis result if analysis succeeded but run failed
      if (action === "Task Start") {
        setAnalysisResult(currentAnalysisResult);
      }
       else {
         setAnalysisResult(null);
       }
      setLatestTaskId(null);
    }
  };

  // Remove formatTimestamp and old result rendering logic

  const isLoading = isAnalyzing || isRunningTask;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit Task Prompt</CardTitle>
        <CardDescription>Enter a prompt for the Upsonic agent to execute using available MCP tools.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handlePromptSubmit} className="space-y-4">
          <Textarea
            ref={textareaRef}
            placeholder="Enter your task prompt here... e.g., 'Summarize the main points on playwright.dev' or 'What are the top 5 stories on Hacker News?'"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            className="min-h-[80px] resize-y"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !prompt.trim()} className="w-full">
            {isAnalyzing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            {isAnalyzing ? "Analyzing..." : (isRunningTask ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />)}
            {isAnalyzing ? "Analyzing..." : (isRunningTask ? "Starting Task..." : "Run Task with Upsonic")}
          </Button>
        </form>

        {(analysisResult || latestTaskId) && (
          <div className="mt-4 space-y-2 rounded-md border bg-muted/50 p-4">
            <h4 className="text-sm font-medium">Task Initiation Details</h4>
            {analysisResult && (
               <p className="text-sm text-muted-foreground">
                 Goal: {analysisResult.goal} <br/>
                 Identified Tools: {analysisResult.requiredTools.length > 0 ? analysisResult.requiredTools.join(', ') : 'None'}
               </p>
            )}
            {latestTaskId && (
              <p className="text-sm font-semibold">
                Task Started ID: <span className="font-mono text-primary">{latestTaskId}</span>
              </p>
            )}
             {!latestTaskId && isRunningTask && (
               <p className="text-sm text-muted-foreground italic">Waiting for task ID...</p>
             )}
             <p className="text-xs text-muted-foreground pt-2">Monitor detailed progress in the 'Tasks' tab.</p>
          </div>
        )}
      </CardContent>
      {/* Remove CardFooter and previous results display */}
    </Card>
    // Remove the second column (previous results/chat display)
  );
} 