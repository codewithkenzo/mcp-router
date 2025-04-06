"use client";

import { useState, useEffect } from "react";
import { useQuery } from "react-query";
import axios from "axios";
import { Search, Star, StarIcon, Sparkles, Zap, Cpu } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { mockModels } from "@/lib/mock-data";

interface Model {
  id: string;
  name: string;
  description: string;
  provider: string;
  capabilities: string[];
  context_length: number;
  pricing: {
    prompt: number;
    completion: number;
  };
}

export default function ModelsTab() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [selectedTab, setSelectedTab] = useState("all");
  const [favorites, setFavorites] = useState<string[]>([]);

  // Provider-specific UI info
  const providerInfo = {
    "OpenAI": { color: "text-green-600", bgColor: "bg-green-50 dark:bg-green-950", borderColor: "border-green-200 dark:border-green-800", icon: <Sparkles className="h-4 w-4 text-green-600" /> },
    "Anthropic": { color: "text-purple-600", bgColor: "bg-purple-50 dark:bg-purple-950", borderColor: "border-purple-200 dark:border-purple-800", icon: <Sparkles className="h-4 w-4 text-purple-600" /> },
    "Meta": { color: "text-blue-600", bgColor: "bg-blue-50 dark:bg-blue-950", borderColor: "border-blue-200 dark:border-blue-800", icon: <Sparkles className="h-4 w-4 text-blue-600" /> },
    "Google": { color: "text-red-600", bgColor: "bg-red-50 dark:bg-red-950", borderColor: "border-red-200 dark:border-red-800", icon: <Sparkles className="h-4 w-4 text-red-600" /> },
    "Mistral AI": { color: "text-sky-600", bgColor: "bg-sky-50 dark:bg-sky-950", borderColor: "border-sky-200 dark:border-sky-800", icon: <Sparkles className="h-4 w-4 text-sky-600" /> },
  };

  // Load favorites from localStorage on component mount
  useEffect(() => {
    const savedFavorites = localStorage.getItem("favoriteModels");
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  // Update localStorage when favorites change
  useEffect(() => {
    localStorage.setItem("favoriteModels", JSON.stringify(favorites));
  }, [favorites]);

  const toggleFavorite = (modelId: string) => {
    setFavorites(prev => {
      if (prev.includes(modelId)) {
        return prev.filter(id => id !== modelId);
      } else {
        return [...prev, modelId];
      }
    });
  };

  // Fetch models - in a real app this would call the API
  const { data: models = [], isLoading, error } = useQuery<Model[]>(
    "models",
    async () => {
      try {
        // Try to fetch from API first
        const response = await axios.get("/api/models");
        return response.data;
      } catch (error) {
        // If API fails, use mock data
        console.log("Using mock models data");
        return mockModels;
      }
    },
    {
      retry: false,
      refetchOnWindowFocus: false,
      onError: () => {
        toast({
          title: "Failed to load available models",
          description: "Using mock data instead. API server may be down.",
          variant: "destructive",
        });
      }
    }
  );

  // Filter models based on search query and active tab
  const filteredModels = models.filter(model => {
    const matchesSearch = 
      model.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      model.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      model.provider.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (selectedTab === "all") return matchesSearch;
    if (selectedTab === "favorites") return matchesSearch && favorites.includes(model.id);
    // Filter by provider
    return matchesSearch && model.provider.toLowerCase().includes(selectedTab.toLowerCase());
  });

  // Get unique providers for tab filtering
  const providers = [...new Set(models.map(model => model.provider))];

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search models..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <Tabs defaultValue="all" value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="mb-4 flex flex-wrap">
          <TabsTrigger value="all" className="rounded-md">All Models</TabsTrigger>
          <TabsTrigger value="favorites" className="rounded-md">
            <StarIcon className="h-4 w-4 mr-1" />
            Favorites
          </TabsTrigger>
          {providers.map(provider => (
            <TabsTrigger key={provider} value={provider.toLowerCase()} className="rounded-md">
              {providerInfo[provider as keyof typeof providerInfo]?.icon}
              <span className="ml-1">{provider}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value={selectedTab} className="mt-0">
          {isLoading ? (
            <div className="flex justify-center items-center h-60">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredModels.length === 0 ? (
            <div className="text-center py-10 text-muted-foreground">
              <p>No models match your search criteria.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredModels.map((model) => {
                const provider = model.provider as keyof typeof providerInfo;
                const isFavorite = favorites.includes(model.id);
                
                return (
                  <div
                    key={model.id}
                    className={`relative p-4 rounded-lg border ${providerInfo[provider]?.borderColor || "border-border"} hover:shadow-md transition-shadow`}
                  >
                    <div className="absolute top-3 right-3">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => toggleFavorite(model.id)}
                        className="h-8 w-8"
                      >
                        {isFavorite ? (
                          <StarIcon className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                        ) : (
                          <Star className="h-5 w-5" />
                        )}
                        <span className="sr-only">Toggle favorite</span>
                      </Button>
                    </div>
                    
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${providerInfo[provider]?.bgColor || "bg-muted"} ${providerInfo[provider]?.color || "text-foreground"}`}>
                        {model.provider}
                      </span>
                      {model.capabilities.includes("vision") && (
                        <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300">
                          Vision
                        </span>
                      )}
                    </div>
                    
                    <h3 className="text-lg font-medium">{model.name}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-2 mt-1 mb-3">{model.description}</p>
                    
                    <div className="flex items-center gap-4 text-xs text-muted-foreground mt-2">
                      <span className="flex items-center gap-1">
                        <Cpu className="h-3 w-3" />
                        {Intl.NumberFormat().format(model.context_length)} tokens
                      </span>
                      <span className="flex items-center gap-1">
                        <Zap className="h-3 w-3" />
                        ${model.pricing.prompt.toFixed(2)}/{model.pricing.completion.toFixed(2)}
                      </span>
                    </div>
                    
                    <Button 
                      className="w-full mt-4"
                      onClick={() => setSelectedModel(model)}
                    >
                      Details
                    </Button>
                  </div>
                );
              })}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Model details dialog */}
      <Dialog open={!!selectedModel} onOpenChange={(open) => !open && setSelectedModel(null)}>
        {selectedModel && (
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>{selectedModel.name}</DialogTitle>
              <DialogDescription>
                <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${providerInfo[selectedModel.provider as keyof typeof providerInfo]?.bgColor || "bg-muted"} ${providerInfo[selectedModel.provider as keyof typeof providerInfo]?.color || "text-foreground"} mr-2`}>
                  {selectedModel.provider}
                </span>
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <p>{selectedModel.description}</p>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <h4 className="text-sm font-medium">Context Length</h4>
                  <p className="text-sm">{Intl.NumberFormat().format(selectedModel.context_length)} tokens</p>
                </div>
                
                <div className="space-y-1">
                  <h4 className="text-sm font-medium">Capabilities</h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedModel.capabilities.map(capability => (
                      <span key={capability} className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-800">
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="space-y-1">
                <h4 className="text-sm font-medium">Pricing (per million tokens)</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex justify-between p-2 border rounded">
                    <span>Prompt</span>
                    <span className="font-medium">${selectedModel.pricing.prompt.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between p-2 border rounded">
                    <span>Completion</span>
                    <span className="font-medium">${selectedModel.pricing.completion.toFixed(2)}</span>
                  </div>
                </div>
              </div>
              
              <div className="pt-4 flex justify-end space-x-2">
                <Button 
                  variant="secondary" 
                  onClick={() => setSelectedModel(null)}
                >
                  Close
                </Button>
                <Button 
                  onClick={() => {
                    toast({
                      title: "Model selected",
                      description: `${selectedModel.name} is now your active model`,
                    });
                    setSelectedModel(null);
                  }}
                >
                  Select Model
                </Button>
              </div>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
} 