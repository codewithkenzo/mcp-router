'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Loader2 } from 'lucide-react';
import { useTasks } from '@/context/TaskContext';

export default function QueryTab() {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const { addTask } = useTasks();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!prompt.trim()) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Prompt cannot be empty.',
      });
      return;
    }

    setIsLoading(true);

    try {
      // Step 1: Call analyze API (currently returns mock data)
      console.log('[QueryTab] Calling /api/upsonic/analyze with prompt:', prompt);
      const analyzeResponse = await fetch('/api/upsonic/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json();
        throw new Error(`Analysis failed: ${analyzeResponse.status} ${analyzeResponse.statusText} - ${errorData?.details || errorData?.error}`);
      }

      const analysisResult = await analyzeResponse.json();
      console.log('[QueryTab] Received analysis result:', analysisResult);

      // Step 2: Call run API with the analysis result (currently returns mock task ID)
      console.log('[QueryTab] Calling /api/upsonic/run with analysis result');
      const runResponse = await fetch('/api/upsonic/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisResult), // Send the whole analysis result
      });

      if (!runResponse.ok) {
        const errorData = await runResponse.json();
        throw new Error(`Run failed: ${runResponse.status} ${runResponse.statusText} - ${errorData?.details || errorData?.error}`);
      }

      const runResult = await runResponse.json();
      console.log('[QueryTab] Received run result:', runResult);
      const taskId = runResult.taskId;

      addTask(taskId);

      toast({
        title: 'Task Started',
        description: `Agent task initiated with ID: ${taskId}. Check the Tasks tab for progress.`,
      });

      // TODO: Optionally navigate to the Tasks tab or update a shared state
      setPrompt(''); // Clear prompt on success

    } catch (error) {
      console.error('[QueryTab] Error submitting task:', error);
      toast({
        variant: 'destructive',
        title: 'Task Submission Failed',
        description: error instanceof Error ? error.message : 'An unknown error occurred.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Initiate Agent Task</CardTitle>
        <CardDescription>Enter a prompt for the agent to execute using available tools.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            placeholder="e.g., Summarize the main points on playwright.dev"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              'Run Task'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
} 