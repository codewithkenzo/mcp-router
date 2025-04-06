"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import axios from "axios";
import { Loader2, Play, Square, RefreshCw, XCircle, Info } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Server {
  id: string;
  description?: string;
  running: boolean;
  metadata?: {
    [key: string]: any;
  };
}

interface AvailableServer {
  id: string;
  description: string;
  version?: string;
  installed: boolean;
}

export default function ServersTab() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<string>("running");
  const [selectedServerId, setSelectedServerId] = useState<string | null>(null);
  const [serverDetails, setServerDetails] = useState<any>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState<boolean>(false);

  // Fetch running servers
  const { 
    data: runningServers = {},
    isLoading: isLoadingServers,
    refetch: refetchServers
  } = useQuery<Record<string, Server>>(
    "servers",
    async () => {
      try {
        const response = await axios.get("/api/servers");
        return response.data || {};
      } catch (error) {
        toast({
          title: "Failed to load servers",
          description: "Could not retrieve running servers. Please try again.",
          variant: "destructive",
        });
        return {};
      }
    }
  );

  // Fetch available servers for installation
  const {
    data: availableServers = [],
    isLoading: isLoadingAvailable,
    refetch: refetchAvailable
  } = useQuery<AvailableServer[]>(
    "available-servers",
    async () => {
      try {
        const response = await axios.get("/api/servers/available");
        return response.data || [];
      } catch (error) {
        toast({
          title: "Failed to load available servers",
          description: "Could not retrieve available servers. Please try again.",
          variant: "destructive",
        });
        return [];
      }
    }
  );

  // Start server mutation
  const startServerMutation = useMutation(
    async (serverId: string) => {
      return await axios.post(`/api/servers/${serverId}/start`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries("servers");
        toast({
          title: "Server started",
          description: "The server has been started successfully.",
        });
      },
      onError: () => {
        toast({
          title: "Failed to start server",
          description: "Could not start the server. Please try again.",
          variant: "destructive",
        });
      }
    }
  );

  // Stop server mutation
  const stopServerMutation = useMutation(
    async (serverId: string) => {
      return await axios.post(`/api/servers/${serverId}/stop`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries("servers");
        toast({
          title: "Server stopped",
          description: "The server has been stopped successfully.",
        });
      },
      onError: () => {
        toast({
          title: "Failed to stop server",
          description: "Could not stop the server. Please try again.",
          variant: "destructive",
        });
      }
    }
  );

  // Install server mutation
  const installServerMutation = useMutation(
    async (serverId: string) => {
      return await axios.post(`/api/servers/${serverId}/install`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries("available-servers");
        toast({
          title: "Server installed",
          description: "The server has been installed successfully.",
        });
      },
      onError: (error: any) => {
        toast({
          title: "Failed to install server",
          description: error.response?.data?.message || "Could not install the server. Please try again.",
          variant: "destructive",
        });
      }
    }
  );

  // Uninstall server mutation
  const uninstallServerMutation = useMutation(
    async (serverId: string) => {
      return await axios.post(`/api/servers/${serverId}/uninstall`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries("available-servers");
        toast({
          title: "Server uninstalled",
          description: "The server has been uninstalled successfully.",
        });
      },
      onError: () => {
        toast({
          title: "Failed to uninstall server",
          description: "Could not uninstall the server. Please try again.",
          variant: "destructive",
        });
      }
    }
  );

  // Fetch server details
  const fetchServerDetails = async (serverId: string) => {
    setSelectedServerId(serverId);
    setIsDetailsOpen(true);
    
    try {
      const response = await axios.get(`/api/servers/${serverId}/details`);
      setServerDetails(response.data);
    } catch (error) {
      setServerDetails(null);
      toast({
        title: "Failed to load server details",
        description: "Could not retrieve server details. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    if (activeTab === "running") {
      refetchServers();
    } else {
      refetchAvailable();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">MCP Servers</h2>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleRefresh}
          disabled={isLoadingServers || isLoadingAvailable}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${(isLoadingServers || isLoadingAvailable) ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Tabs 
        defaultValue="running" 
        value={activeTab} 
        onValueChange={setActiveTab}
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="running">Running Servers</TabsTrigger>
          <TabsTrigger value="available">Available Servers</TabsTrigger>
        </TabsList>

        {/* Running Servers Tab */}
        <TabsContent value="running" className="py-4">
          {isLoadingServers ? (
            <div className="flex justify-center items-center h-40">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : Object.keys(runningServers).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(runningServers).map(([id, server]) => (
                <Card key={id} className="overflow-hidden">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{id}</CardTitle>
                        {server.description && (
                          <CardDescription>{server.description}</CardDescription>
                        )}
                      </div>
                      <Badge variant={server.running ? "default" : "secondary"}>
                        {server.running ? "Running" : "Stopped"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pb-2">
                    {server.metadata && (
                      <div className="text-sm text-muted-foreground">
                        <p>Version: {server.metadata.version || "Unknown"}</p>
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="flex justify-between pt-2">
                    <div className="flex space-x-2">
                      {server.running ? (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => stopServerMutation.mutate(id)}
                          disabled={stopServerMutation.isLoading}
                        >
                          {stopServerMutation.isLoading && id === selectedServerId ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          ) : (
                            <Square className="mr-2 h-4 w-4" />
                          )}
                          Stop
                        </Button>
                      ) : (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => {
                            setSelectedServerId(id);
                            startServerMutation.mutate(id);
                          }}
                          disabled={startServerMutation.isLoading}
                        >
                          {startServerMutation.isLoading && id === selectedServerId ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          ) : (
                            <Play className="mr-2 h-4 w-4" />
                          )}
                          Start
                        </Button>
                      )}
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => fetchServerDetails(id)}
                            >
                              <Info className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>View server details</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                  </CardFooter>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-10">
              <p className="text-muted-foreground">No running servers available.</p>
              <p className="text-sm text-muted-foreground mt-1">
                Go to the "Available Servers" tab to install and start a server.
              </p>
            </div>
          )}
        </TabsContent>

        {/* Available Servers Tab */}
        <TabsContent value="available" className="py-4">
          {isLoadingAvailable ? (
            <div className="flex justify-center items-center h-40">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : availableServers.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {availableServers.map((server) => (
                <Card key={server.id} className="overflow-hidden">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{server.id}</CardTitle>
                        {server.description && (
                          <CardDescription>{server.description}</CardDescription>
                        )}
                      </div>
                      <Badge variant={server.installed ? "default" : "secondary"}>
                        {server.installed ? "Installed" : "Not Installed"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pb-2">
                    {server.version && (
                      <div className="text-sm text-muted-foreground">
                        <p>Version: {server.version}</p>
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="flex justify-between pt-2">
                    <div className="flex space-x-2">
                      {server.installed ? (
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={() => {
                            setSelectedServerId(server.id);
                            uninstallServerMutation.mutate(server.id);
                          }}
                          disabled={uninstallServerMutation.isLoading}
                        >
                          {uninstallServerMutation.isLoading && server.id === selectedServerId ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          ) : (
                            <XCircle className="mr-2 h-4 w-4" />
                          )}
                          Uninstall
                        </Button>
                      ) : (
                        <Button 
                          variant="default" 
                          size="sm"
                          onClick={() => {
                            setSelectedServerId(server.id);
                            installServerMutation.mutate(server.id);
                          }}
                          disabled={installServerMutation.isLoading}
                        >
                          {installServerMutation.isLoading && server.id === selectedServerId ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          ) : (
                            <Play className="mr-2 h-4 w-4" />
                          )}
                          Install
                        </Button>
                      )}
                    </div>
                  </CardFooter>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-10">
              <p className="text-muted-foreground">No servers available for installation.</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Server Details Dialog */}
      <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{selectedServerId} Details</DialogTitle>
            <DialogDescription>
              Detailed information about the server.
            </DialogDescription>
          </DialogHeader>
          
          {serverDetails ? (
            <ScrollArea className="max-h-96">
              <div className="space-y-4">
                {Object.entries(serverDetails).map(([key, value]) => (
                  <div key={key}>
                    <h4 className="font-medium">{key}</h4>
                    <pre className="bg-muted p-2 rounded-md text-xs overflow-x-auto mt-1">
                      {typeof value === 'object' 
                        ? JSON.stringify(value, null, 2) 
                        : String(value)
                      }
                    </pre>
                  </div>
                ))}
              </div>
            </ScrollArea>
          ) : (
            <div className="flex justify-center items-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 