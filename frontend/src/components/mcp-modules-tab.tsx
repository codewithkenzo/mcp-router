"use client";

import { useState, useEffect } from "react";
import { useQuery } from "react-query";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  Tabs, 
  TabsList, 
  TabsTrigger, 
  TabsContent 
} from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { 
  Download, 
  Github, 
  Settings, 
  Search, 
  Info, 
  Plus, 
  Check, 
  AlertCircle,
  Terminal,
  Database
} from "lucide-react";
import { mcpService, Module as MCPModule } from "@/lib/mcp-service";
import { downloadConfigScript, markModuleAsInstalled, getInstalledModules } from "@/lib/mcp-utils";

// Define module interfaces
interface ModuleConfig {
  type: string;
  description: string;
  required_error?: string;
}

export default function MCPModulesTab() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedModule, setSelectedModule] = useState<MCPModule | null>(null);
  const [configOpen, setConfigOpen] = useState(false);
  const [configValues, setConfigValues] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState("recommended");

  // Fetch built-in modules
  const { 
    data: builtInModules = [], 
    isLoading: isLoadingBuiltIn 
  } = useQuery("built-in-modules", mcpService.fetchBuiltInModules);

  // Fetch community modules
  const { 
    data: communityModules = [], 
    isLoading: isLoadingCommunity 
  } = useQuery("community-modules", mcpService.fetchCommunityModules);

  // Fetch marketplace modules
  const { 
    data: marketplaceModules = [], 
    isLoading: isLoadingMarket
  } = useQuery("marketplace-modules", mcpService.fetchModules, {
    refetchOnWindowFocus: false,
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  // Filter modules based on search query
  const filteredBuiltIn = builtInModules.filter(module => 
    module.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    module.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    module.keywords.some(keyword => keyword.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const filteredCommunity = communityModules.filter(module => 
    module.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    module.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    module.keywords.some(keyword => keyword.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleInstall = (module: MCPModule) => {
    // Check if module has config schema
    if (module.configSchema && Object.keys(module.configSchema).length > 0) {
      setSelectedModule(module);
      setConfigOpen(true);
      // Initialize config values
      const initialValues: Record<string, string> = {};
      if (module.configSchema) {
        Object.keys(module.configSchema).forEach(key => {
          initialValues[key] = "";
        });
      }
      setConfigValues(initialValues);
    } else {
      // Direct install without config
      mcpService.installModule(module).then(success => {
        if (success) {
          // Generate and download the configuration script
          downloadConfigScript(module, {});
          // Mark the module as installed locally
          markModuleAsInstalled(module.name);
        }
      });
    }
  };

  const handleConfigSubmit = () => {
    if (!selectedModule) return;
    
    mcpService.installModule(selectedModule, configValues).then(success => {
      if (success) {
        // Generate and download the configuration script
        downloadConfigScript(selectedModule, configValues);
        // Mark the module as installed locally
        markModuleAsInstalled(selectedModule.name);
        setConfigOpen(false);
      }
    });
  };

  const handleConfigChange = (key: string, value: string): void => {
    setConfigValues(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleAddModule = () => {
    // In a real implementation, this would open a dialog to add a custom module
    toast({
      title: "Coming Soon",
      description: "Custom module addition will be available in a future update.",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-4">
        <h2 className="text-2xl font-bold">MCP Modules</h2>
        <p className="text-muted-foreground">
          Install and manage Model Context Protocol modules to extend functionality
        </p>
        
        <div className="flex items-center space-x-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search modules..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button variant="outline" onClick={handleAddModule}>
            <Plus className="mr-2 h-4 w-4" />
            Add MCP
          </Button>
        </div>
      </div>

      <Tabs 
        defaultValue="recommended" 
        className="w-full"
        onValueChange={(value) => setActiveTab(value)}
      >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="recommended">
            HyperChat Recommend List
          </TabsTrigger>
          <TabsTrigger value="community">
            MCP Community
          </TabsTrigger>
        </TabsList>

        <TabsContent value="recommended" className="pt-4">
          {isLoadingBuiltIn ? (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredBuiltIn.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10">
              <AlertCircle className="h-10 w-10 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No built-in modules match your search.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {filteredBuiltIn.map((module) => (
                <Card key={module.name}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-base">{module.name.replace(/_/g, " ")}</CardTitle>
                      <div className="px-2 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                        {module.status}
                      </div>
                    </div>
                    <CardDescription className="text-xs">{module.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="pb-2">
                    <div className="flex flex-wrap gap-1">
                      {module.keywords.map((keyword) => (
                        <span 
                          key={keyword} 
                          className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-800"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                  <CardFooter className="pt-0 flex justify-between">
                    <Button variant="outline" size="sm" disabled>
                      <Settings className="h-4 w-4 mr-1" />
                      Configure
                    </Button>
                    <div className="flex items-center space-x-1">
                      <Check className="h-4 w-4 text-green-500" />
                      <span className="text-xs text-muted-foreground">Installed</span>
                    </div>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="community" className="pt-4">
          {isLoadingCommunity ? (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredCommunity.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10">
              <AlertCircle className="h-10 w-10 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No community modules match your search.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {filteredCommunity.map((module) => (
                <Card key={module.name}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-base">{module.name}</CardTitle>
                      {module.status === 'installed' ? (
                        <div className="px-2 py-1 text-xs rounded-full bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                          installed
                        </div>
                      ) : (
                        <div className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
                          available
                        </div>
                      )}
                    </div>
                    <CardDescription className="text-xs">{module.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="pb-2">
                    <div className="flex flex-wrap gap-1">
                      {module.keywords.map((keyword) => (
                        <span 
                          key={keyword} 
                          className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-800"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                  <CardFooter className="pt-0 flex justify-between">
                    {module.github && (
                      <Button variant="outline" size="sm" asChild>
                        <a href={module.github} target="_blank" rel="noopener noreferrer">
                          <Github className="h-4 w-4 mr-1" />
                          GitHub
                        </a>
                      </Button>
                    )}
                    {!module.github && (
                      <Button variant="outline" size="sm" disabled>
                        <Info className="h-4 w-4 mr-1" />
                        Info
                      </Button>
                    )}
                    {module.status === 'installed' ? (
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4 mr-1" />
                        Configure
                      </Button>
                    ) : (
                      <Button size="sm" onClick={() => handleInstall(module)}>
                        <Download className="h-4 w-4 mr-1" />
                        Install
                      </Button>
                    )}
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Module Configuration Dialog */}
      <Dialog open={configOpen} onOpenChange={setConfigOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Configure MCP</DialogTitle>
            <DialogDescription>
              Configure the module before installation.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-right">
                Name <span className="text-red-500">*</span>
              </Label>
              <Input id="name" placeholder="Please enter" />
            </div>
            
            <div className="space-y-2">
              <Label className="text-right">
                type <span className="text-red-500">*</span>
              </Label>
              <div className="flex gap-4">
                <div className="flex items-center space-x-2">
                  <input type="radio" id="stdin" name="type" value="stdin" defaultChecked />
                  <Label htmlFor="stdin">stdin</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input type="radio" id="sse" name="type" value="sse" />
                  <Label htmlFor="sse">sse</Label>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="command" className="text-right">
                command <span className="text-red-500">*</span>
              </Label>
              <Input id="command" placeholder="Please enter command" />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="env" className="text-right">
                env
              </Label>
              <div className="border rounded-md p-2">
                <Button variant="outline" className="w-full flex justify-center" type="button">
                  <Plus className="h-4 w-4 mr-2" /> Add Environment Variables
                </Button>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button type="submit" onClick={handleConfigSubmit}>
              Install And Run
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Market modules section - for future implementation */}
      <div className="mt-6">
        <h3 className="text-xl font-semibold mb-4">More MCP Market</h3>
        <div className="flex flex-col space-y-2">
          <a href="https://modelcontextprotocol.ai" className="text-blue-500 hover:underline">modelcontextprotocol.ai</a>
          <a href="https://mcp.so" className="text-blue-500 hover:underline">mcp.so</a>
          <a href="https://pulsemcp.com" className="text-blue-500 hover:underline">pulsemcp.com</a>
          <a href="https://glama.ai" className="text-blue-500 hover:underline">glama.ai</a>
          <a href="https://smithery.ai" className="text-blue-500 hover:underline">smithery.ai</a>
        </div>
        
        <div className="mt-4">
          <h4 className="font-medium">Help:</h4>
          <div className="flex flex-col space-y-1 text-sm text-muted-foreground">
            <div>nodejs: v23.9.0</div>
            <div>uv: uv 0.6.12</div>
          </div>
          <Button variant="outline" className="mt-2 text-red-500" size="sm">
            Try Repair environment
          </Button>
        </div>
      </div>
    </div>
  );
} 