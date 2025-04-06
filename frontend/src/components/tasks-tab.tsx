"use client";

import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Loader2, Info, CheckCircle2, XCircle, Hourglass, ServerCrash, RefreshCw } from "lucide-react";
import { useTasks } from "@/context/TaskContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ScrollArea } from "@/components/ui/scroll-area";

interface TaskStep {
  timestamp: string;
  message: string;
}

interface UpsonicTaskStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  goal: string;
  tools: string[];
  steps: TaskStep[];
  result: any | null;
  error: string | null;
  createdAt: string;
}

const POLLING_INTERVAL = 5000;

export default function TasksTab() {
  const { taskIds } = useTasks();
  const { toast } = useToast();
  const [taskStates, setTaskStates] = useState<{ [taskId: string]: UpsonicTaskStatus }>({});
  const [isLoadingInitial, setIsLoadingInitial] = useState<boolean>(false);
  const [loadingStates, setLoadingStates] = useState<{ [taskId: string]: boolean }>({});

  const fetchTaskStatus = useCallback(async (taskId: string, isManualRefresh = false) => {
    if (!isManualRefresh) {
        const isInitialFetch = !taskStates[taskId];
        if (isInitialFetch) setLoadingStates(prev => ({ ...prev, [taskId]: true }));
    } else {
         setLoadingStates(prev => ({ ...prev, [taskId]: true }));
    }

    try {
      const response = await axios.get(`/api/upsonic/status/${taskId}`);
      setTaskStates(prev => ({
        ...prev,
        [taskId]: response.data,
      }));
    } catch (error: any) {
      console.error(`Error fetching status for task ${taskId}:`, error);
       if (error.response?.status === 404) {
           setTaskStates(prev => {
               const newState = {...prev};
               const errorMsg = "Task not found on server (404). Might be completed or expired.";
               if(newState[taskId]) {
                  newState[taskId].error = errorMsg;
                  newState[taskId].status = 'failed';
               } else {
                  newState[taskId] = { id: taskId, status: 'failed', error: errorMsg, createdAt: new Date().toISOString() } as Partial<UpsonicTaskStatus> as UpsonicTaskStatus;
               }
               return newState;
           });
       } else {
            const errorMsg = `Failed to fetch status: ${error.message || 'Unknown error'}`;
            setTaskStates(prev => {
               const newState = {...prev};
               if(newState[taskId]) {
                   newState[taskId].error = errorMsg
               } else {
                  newState[taskId] = { id: taskId, status: 'failed', error: errorMsg, createdAt: new Date().toISOString() } as Partial<UpsonicTaskStatus> as UpsonicTaskStatus;
               }
               return newState;
            });
             if (isManualRefresh) {
                  toast({
                       title: `Status Fetch Failed (Task ${taskId.substring(0, 6)}...)`,
                       description: error.message || "Could not fetch task status.",
                       variant: "destructive",
                  });
             }
       }
    } finally {
       if (isManualRefresh || !taskStates[taskId]) {
           setLoadingStates(prev => ({ ...prev, [taskId]: false }));
       }
    }
  }, [toast]);

  useEffect(() => {
    const tasksToFetch = taskIds.filter(id => !taskStates[id]);
    if (tasksToFetch.length > 0) {
      setIsLoadingInitial(true);
      const fetchAllNew = async () => {
        await Promise.all(tasksToFetch.map(id => fetchTaskStatus(id)));
        setIsLoadingInitial(false);
      };
      fetchAllNew();
    }
  }, [taskIds]);

  useEffect(() => {
    const activeTaskIds = taskIds.filter(id => {
        const state = taskStates[id];
        return !state || state.status === 'pending' || state.status === 'running';
    });

    if (activeTaskIds.length === 0) return;

    const intervalId = setInterval(() => {
      activeTaskIds.forEach(id => fetchTaskStatus(id));
    }, POLLING_INTERVAL);

    return () => clearInterval(intervalId);
  }, [taskIds, taskStates, fetchTaskStatus]);

 const getStatusBadge = (status: UpsonicTaskStatus['status'] | undefined) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary"><Hourglass className="mr-1 h-3 w-3" /> Pending</Badge>;
      case 'running':
        return <Badge variant="outline" className="text-blue-600 border-blue-600"><Loader2 className="mr-1 h-3 w-3 animate-spin" /> Running</Badge>;
      case 'completed':
        return <Badge variant="default" className="bg-green-600 hover:bg-green-700"><CheckCircle2 className="mr-1 h-3 w-3" /> Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" /> Failed</Badge>;
      default:
        return <Badge variant="secondary">Loading...</Badge>;
    }
  };

  const handleRefreshTask = (taskId: string) => {
      fetchTaskStatus(taskId, true);
  };

  return (
    <div className="space-y-4">
       <Card>
         <CardHeader>
           <div className="flex justify-between items-center">
             <div>
                 <CardTitle>Upsonic Task Monitor</CardTitle>
                 <CardDescription>View the status and results of tasks initiated via prompts.</CardDescription>
             </div>
           </div>
         </CardHeader>
         <CardContent>
           {(isLoadingInitial && taskIds.length === 0) && (
              <div className="flex justify-center items-center p-8">
                 <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
           )}
           {!isLoadingInitial && taskIds.length === 0 && (
              <p className="text-center text-muted-foreground p-8">No tasks initiated yet. Submit a prompt in the 'Query' tab.</p>
           )}

           {taskIds.length > 0 && (
             <Accordion type="multiple" className="w-full space-y-2">
               {taskIds.map((taskId) => {
                 const task = taskStates[taskId];
                 const isTaskLoading = loadingStates[taskId] ?? !task;

                 const goalDisplay = task?.goal ?? (isTaskLoading ? 'Loading...' : 'Unknown Goal');

                 return (
                   <AccordionItem value={taskId} key={taskId} className="border rounded-md px-4 bg-background">
                     <AccordionTrigger className="hover:no-underline py-3">
                       <div className="flex justify-between items-center w-full gap-2">
                         <div className="flex flex-col items-start text-left overflow-hidden mr-2">
                            <span className="font-mono text-sm text-primary truncate" title={taskId}>
                                ID: {taskId}
                            </span>
                            <span className="text-xs text-muted-foreground truncate" title={goalDisplay}>
                                Goal: {goalDisplay}
                            </span>
                         </div>
                         <div className="flex items-center gap-2 ml-auto flex-shrink-0">
                            {getStatusBadge(task?.status)}
                            <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); handleRefreshTask(taskId); }} disabled={isTaskLoading} title="Refresh Status">
                               <RefreshCw className={`h-4 w-4 ${isTaskLoading ? 'animate-spin' : ''}`} />
                            </Button>
                         </div>
                       </div>
                     </AccordionTrigger>
                     <AccordionContent className="pt-2 pb-4">
                       {task ? (
                         <div className="space-y-3 text-sm">
                            <p><strong className="font-medium">Tools:</strong> {task.tools?.join(', ') || 'N/A'}</p>
                            <p><strong className="font-medium">Created:</strong> {task.createdAt ? new Date(task.createdAt).toLocaleString() : 'N/A'}</p>
                            {task.error && (
                                <div className="mt-2 p-2 border border-destructive/50 bg-destructive/10 rounded-md">
                                 <p className="text-destructive font-medium flex items-center"><ServerCrash className="h-4 w-4 mr-2 flex-shrink-0"/> Error:</p>
                                 <p className="text-destructive/90 text-xs pl-6 whitespace-pre-wrap">{task.error}</p>
                                </div>
                            )}
                            {task.steps && task.steps.length > 0 && (
                             <div>
                               <h4 className="font-medium mb-1">Steps / Logs:</h4>
                               <ScrollArea className="h-[150px] border rounded-md p-2 bg-muted/50">
                                <div className="space-y-1 text-xs font-mono">
                                   {task.steps.map((step, index) => (
                                     <p key={index}>
                                       <span className="text-muted-foreground">[{step.timestamp ? new Date(step.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '?'}]</span> {step.message}
                                     </p>
                                   ))}
                                 </div>
                               </ScrollArea>
                             </div>
                           )}
                            {task.status === 'completed' && task.result != null && (
                             <div>
                               <h4 className="font-medium mb-1">Result:</h4>
                               <pre className="text-xs bg-muted/50 border rounded-md p-2 overflow-auto max-h-[200px]">
                                 {typeof task.result === 'string' ? task.result : JSON.stringify(task.result, null, 2)}
                               </pre>
                             </div>
                           )}
                         </div>
                       ) : (
                         <div className="flex items-center justify-center p-4">
                            <Loader2 className="h-4 w-4 mr-2 animate-spin"/>
                            <p className="text-muted-foreground text-sm italic">Loading task details...</p>
                         </div>
                       )}
                     </AccordionContent>
                   </AccordionItem>
                 );
               })}
             </Accordion>
           )}
         </CardContent>
       </Card>
    </div>
  );
} 