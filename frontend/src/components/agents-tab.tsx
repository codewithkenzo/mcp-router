"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import axios from "axios";
import { 
  Plus, 
  Pencil, 
  Trash2, 
  Bot, 
  ChevronRight,
  Search
} from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter,
  DialogDescription,
  DialogClose
} from "@/components/ui/dialog";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { mockAgentTemplates, mockAvailableTools, mockModels } from "@/lib/mock-data";

// Define interfaces for agent data
interface Agent {
  id: string;
  name: string;
  description: string;
  type: string;
  config: {
    model: string;
    parameters: {
      temperature: number;
      max_tokens: number;
      [key: string]: any;
    };
    tools: string[];
    description: string;
  };
  created_at: string;
}

// Mock data for demonstration
const mockAgents: Agent[] = [
  {
    id: "research-agent-1",
    name: "Research Assistant",
    description: "Helps with research tasks and web searches",
    type: "researcher",
    config: {
      model: "anthropic/claude-3-sonnet",
      parameters: {
        temperature: 0.7,
        max_tokens: 4000
      },
      tools: ["web_search", "read_file", "summarize"],
      description: "Research assistant capable of searching the web and analyzing information"
    },
    created_at: "2023-12-10T08:00:00Z"
  },
  {
    id: "code-agent-1",
    name: "Code Helper",
    description: "Assists with code generation and analysis",
    type: "coder",
    config: {
      model: "anthropic/claude-3-opus",
      parameters: {
        temperature: 0.2,
        max_tokens: 8000
      },
      tools: ["read_file", "write_file", "execute_code", "search_code"],
      description: "Coding assistant with file access and execution capabilities"
    },
    created_at: "2023-12-15T10:30:00Z"
  }
];

export default function AgentsTab() {
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  
  // Form state for creating/editing agents
  const [agentName, setAgentName] = useState("");
  const [agentDescription, setAgentDescription] = useState("");
  const [agentType, setAgentType] = useState("");
  const [agentConfig, setAgentConfig] = useState<any>({
    model: "",
    parameters: {
      temperature: 0.5,
      max_tokens: 4000
    },
    tools: [],
    description: ""
  });

  // Fetch agents
  const { data: agents = [], isLoading: isLoadingAgents } = useQuery<Agent[]>(
    "agents",
    async () => {
      try {
        const response = await axios.get("/api/agents");
        return response.data;
      } catch (error) {
        // Return mock data if API fails
        console.log("Using mock agents data");
        return mockAgents;
      }
    },
    {
      retry: false,
      refetchOnWindowFocus: false,
      onError: () => {
        toast({
          title: "Failed to load available agents",
          description: "Using mock data instead. API server may be down.",
          variant: "destructive",
        });
      }
    }
  );

  // Fetch agent templates
  const { data: agentTemplates = [], isLoading: isLoadingTemplates } = useQuery(
    "agentTemplates",
    async () => {
      try {
        const response = await axios.get("/api/agent-templates");
        return response.data;
      } catch (error) {
        return mockAgentTemplates;
      }
    },
    {
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  // Fetch available tools
  const { data: availableTools = [], isLoading: isLoadingTools } = useQuery(
    "tools",
    async () => {
      try {
        const response = await axios.get("/api/tools");
        return response.data;
      } catch (error) {
        return mockAvailableTools;
      }
    },
    {
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  // Fetch available models
  const { data: availableModels = [] } = useQuery(
    "models",
    async () => {
      try {
        const response = await axios.get("/api/models");
        return response.data;
      } catch (error) {
        return mockModels;
      }
    },
    {
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  // Mutations for agent operations
  const createAgentMutation = useMutation(
    async (newAgent: Omit<Agent, "id" | "created_at">) => {
      try {
        const response = await axios.post("/api/agents", newAgent);
        return response.data;
      } catch (error) {
        // For demo, simulate successful creation with mock data
        return {
          ...newAgent,
          id: `agent-${Date.now()}`,
          created_at: new Date().toISOString()
        };
      }
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries("agents");
        toast({
          title: "Agent created",
          description: "The agent has been created successfully",
        });
        resetForm();
        setIsCreateDialogOpen(false);
      },
      onError: (error: any) => {
        toast({
          title: "Failed to create agent",
          description: error.message || "An error occurred while creating the agent",
          variant: "destructive",
        });
      },
    }
  );

  const updateAgentMutation = useMutation(
    async (updatedAgent: Agent) => {
      try {
        const response = await axios.put(`/api/agents/${updatedAgent.id}`, updatedAgent);
        return response.data;
      } catch (error) {
        // For demo, simulate successful update
        return updatedAgent;
      }
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries("agents");
        toast({
          title: "Agent updated",
          description: "The agent has been updated successfully",
        });
        resetForm();
        setIsEditDialogOpen(false);
      },
      onError: (error: any) => {
        toast({
          title: "Failed to update agent",
          description: error.message || "An error occurred while updating the agent",
          variant: "destructive",
        });
      },
    }
  );

  const deleteAgentMutation = useMutation(
    async (agentId: string) => {
      try {
        await axios.delete(`/api/agents/${agentId}`);
        return agentId;
      } catch (error) {
        // For demo, simulate successful deletion
        return agentId;
      }
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries("agents");
        toast({
          title: "Agent deleted",
          description: "The agent has been deleted successfully",
        });
        setIsDeleteDialogOpen(false);
      },
      onError: (error: any) => {
        toast({
          title: "Failed to delete agent",
          description: error.message || "An error occurred while deleting the agent",
          variant: "destructive",
        });
      },
    }
  );

  // Filter agents based on search query
  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Reset form state
  const resetForm = () => {
    setAgentName("");
    setAgentDescription("");
    setAgentType("");
    setAgentConfig({
      model: "",
      parameters: {
        temperature: 0.5,
        max_tokens: 4000
      },
      tools: [],
      description: ""
    });
  };

  // Handle agent type selection and load template config
  const handleAgentTypeSelect = (type: string) => {
    setAgentType(type);
    
    // Find the template for this agent type
    const template = agentTemplates.find((t: any) => t.id === type);
    if (template && template.config_template) {
      setAgentConfig({
        ...template.config_template,
        tools: [...template.config_template.tools]
      });
    }
  };

  // Handle tool selection
  const handleToolToggle = (toolId: string) => {
    setAgentConfig(prevConfig => {
      const tools = prevConfig.tools.includes(toolId)
        ? prevConfig.tools.filter((id: string) => id !== toolId)
        : [...prevConfig.tools, toolId];
      
      return { ...prevConfig, tools };
    });
  };

  // Update config with new values
  const handleConfigUpdate = (key: string, value: any) => {
    setAgentConfig(prevConfig => {
      if (key.startsWith("parameters.")) {
        const paramKey = key.split(".")[1];
        return {
          ...prevConfig,
          parameters: {
            ...prevConfig.parameters,
            [paramKey]: value
          }
        };
      }
      return { ...prevConfig, [key]: value };
    });
  };

  // Handle create agent form submission
  const handleCreateAgent = () => {
    const newAgent = {
      name: agentName,
      description: agentDescription,
      type: agentType,
      config: agentConfig
    };

    createAgentMutation.mutate(newAgent);
  };

  // Handle edit agent form submission
  const handleUpdateAgent = () => {
    if (!selectedAgent) return;

    const updatedAgent = {
      ...selectedAgent,
      name: agentName,
      description: agentDescription,
      type: agentType,
      config: agentConfig
    };

    updateAgentMutation.mutate(updatedAgent);
  };

  // Open edit dialog with selected agent data
  const openEditDialog = (agent: Agent) => {
    setSelectedAgent(agent);
    setAgentName(agent.name);
    setAgentDescription(agent.description);
    setAgentType(agent.type);
    setAgentConfig(agent.config);
    setIsEditDialogOpen(true);
  };

  // Open delete dialog with selected agent
  const openDeleteDialog = (agent: Agent) => {
    setSelectedAgent(agent);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="p-4 space-y-6">
      <div className="flex justify-between items-center mb-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search agents..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button 
          onClick={() => {
            resetForm();
            setIsCreateDialogOpen(true);
          }}
          className="ml-4"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Agent
        </Button>
      </div>

      {isLoadingAgents ? (
        <div className="flex justify-center items-center h-60">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : filteredAgents.length === 0 ? (
        <div className="text-center py-10 border rounded-lg">
          <Bot className="h-10 w-10 mx-auto text-muted-foreground" />
          <p className="mt-4 text-muted-foreground">No agents found.</p>
          <Button 
            onClick={() => {
              resetForm();
              setIsCreateDialogOpen(true);
            }}
            className="mt-4"
            variant="outline"
          >
            Create your first agent
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAgents.map((agent) => (
            <Card key={agent.id} className="overflow-hidden">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between">
                  <span className="truncate">{agent.name}</span>
                  <div className="flex items-center space-x-1">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEditDialog(agent)}>
                            <Pencil className="h-4 w-4" />
                            <span className="sr-only">Edit</span>
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Edit agent</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                    
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openDeleteDialog(agent)}>
                            <Trash2 className="h-4 w-4" />
                            <span className="sr-only">Delete</span>
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Delete agent</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </CardTitle>
                <CardDescription className="truncate">{agent.description}</CardDescription>
              </CardHeader>
              <CardContent className="pb-2">
                <div className="text-sm text-muted-foreground">
                  <div className="flex justify-between my-1">
                    <span>Type:</span>
                    <span className="font-medium capitalize">{agent.type}</span>
                  </div>
                  <div className="flex justify-between my-1">
                    <span>Model:</span>
                    <span className="font-medium">{agent.config.model.split('/').pop()}</span>
                  </div>
                  <div className="flex justify-between my-1">
                    <span>Tools:</span>
                    <span className="font-medium">{agent.config.tools.length}</span>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="pt-1">
                <Button variant="outline" size="sm" className="w-full">
                  <Bot className="h-4 w-4 mr-2" />
                  Configure
                  <ChevronRight className="h-4 w-4 ml-auto" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Create Agent Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Create New Agent</DialogTitle>
            <DialogDescription>
              Configure a new agent for your specific tasks
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="grid gap-3">
                <Label htmlFor="agent-name">Agent Name</Label>
                <Input
                  id="agent-name"
                  placeholder="Name your agent"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                />
              </div>
              
              <div className="grid gap-3">
                <Label htmlFor="agent-description">Description</Label>
                <Textarea
                  id="agent-description"
                  placeholder="Describe what this agent does"
                  value={agentDescription}
                  onChange={(e) => setAgentDescription(e.target.value)}
                />
              </div>
              
              <div className="grid gap-3">
                <Label htmlFor="agent-type">Agent Type</Label>
                <Select
                  value={agentType}
                  onValueChange={handleAgentTypeSelect}
                >
                  <SelectTrigger id="agent-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {agentTemplates.map((template: any) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {agentType && (
                <>
                  <div className="grid gap-3">
                    <Label htmlFor="agent-model">Model</Label>
                    <Select
                      value={agentConfig.model}
                      onValueChange={(value) => handleConfigUpdate("model", value)}
                    >
                      <SelectTrigger id="agent-model">
                        <SelectValue placeholder="Select model" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableModels.map((model: any) => (
                          <SelectItem key={model.id} value={model.id}>
                            {model.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="grid gap-3">
                    <Label>Tools</Label>
                    <ScrollArea className="h-36 border rounded-md p-2">
                      <div className="space-y-2">
                        {availableTools.map((tool: any) => (
                          <div key={tool.id} className="flex items-center space-x-2">
                            <Checkbox 
                              id={`tool-${tool.id}`} 
                              checked={agentConfig.tools.includes(tool.id)}
                              onCheckedChange={() => handleToolToggle(tool.id)}
                            />
                            <Label htmlFor={`tool-${tool.id}`} className="font-normal cursor-pointer">
                              {tool.name}
                              <span className="text-xs block text-muted-foreground">{tool.description}</span>
                            </Label>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </div>
                  
                  <div className="grid gap-3">
                    <Label htmlFor="temperature">Temperature ({agentConfig.parameters.temperature})</Label>
                    <Input
                      id="temperature"
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={agentConfig.parameters.temperature}
                      onChange={(e) => handleConfigUpdate("parameters.temperature", parseFloat(e.target.value))}
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Precise</span>
                      <span>Creative</span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
          
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button 
              onClick={handleCreateAgent}
              disabled={!agentName || !agentType || !agentConfig.model}
            >
              Create Agent
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Agent Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Edit Agent</DialogTitle>
            <DialogDescription>
              Modify your agent's configuration
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="grid gap-3">
                <Label htmlFor="edit-agent-name">Agent Name</Label>
                <Input
                  id="edit-agent-name"
                  placeholder="Name your agent"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                />
              </div>
              
              <div className="grid gap-3">
                <Label htmlFor="edit-agent-description">Description</Label>
                <Textarea
                  id="edit-agent-description"
                  placeholder="Describe what this agent does"
                  value={agentDescription}
                  onChange={(e) => setAgentDescription(e.target.value)}
                />
              </div>
              
              <div className="grid gap-3">
                <Label htmlFor="edit-agent-type">Agent Type</Label>
                <Select
                  value={agentType}
                  onValueChange={handleAgentTypeSelect}
                >
                  <SelectTrigger id="edit-agent-type">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {agentTemplates.map((template: any) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-3">
                <Label htmlFor="edit-agent-model">Model</Label>
                <Select
                  value={agentConfig.model}
                  onValueChange={(value) => handleConfigUpdate("model", value)}
                >
                  <SelectTrigger id="edit-agent-model">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels.map((model: any) => (
                      <SelectItem key={model.id} value={model.id}>
                        {model.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid gap-3">
                <Label>Tools</Label>
                <ScrollArea className="h-36 border rounded-md p-2">
                  <div className="space-y-2">
                    {availableTools.map((tool: any) => (
                      <div key={tool.id} className="flex items-center space-x-2">
                        <Checkbox 
                          id={`edit-tool-${tool.id}`} 
                          checked={agentConfig.tools.includes(tool.id)}
                          onCheckedChange={() => handleToolToggle(tool.id)}
                        />
                        <Label htmlFor={`edit-tool-${tool.id}`} className="font-normal cursor-pointer">
                          {tool.name}
                          <span className="text-xs block text-muted-foreground">{tool.description}</span>
                        </Label>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
              
              <div className="grid gap-3">
                <Label htmlFor="edit-temperature">Temperature ({agentConfig.parameters.temperature})</Label>
                <Input
                  id="edit-temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={agentConfig.parameters.temperature}
                  onChange={(e) => handleConfigUpdate("parameters.temperature", parseFloat(e.target.value))}
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Precise</span>
                  <span>Creative</span>
                </div>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button 
              onClick={handleUpdateAgent}
              disabled={!agentName || !agentType || !agentConfig.model}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Agent</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this agent? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          
          {selectedAgent && (
            <div className="py-3">
              <p className="font-medium">{selectedAgent.name}</p>
              <p className="text-sm text-muted-foreground">{selectedAgent.description}</p>
            </div>
          )}
          
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button 
              variant="destructive" 
              onClick={() => selectedAgent && deleteAgentMutation.mutate(selectedAgent.id)}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 