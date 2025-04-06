"use client";

import { useState } from "react";
import { QueryClient, QueryClientProvider } from "react-query";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Toaster } from "@/components/ui/toaster";
import { ThemeProvider } from "next-themes";

import QueryTab from "@/components/tabs/QueryTab";
import ServersTab from "@/components/servers-tab";
import ModelsTab from "@/components/models-tab";
import TasksTab from "@/components/tasks-tab";
import AgentsTab from "@/components/agents-tab";
import SettingsTab from "@/components/settings-tab";
import MCPModulesTab from "@/components/mcp-modules-tab";
import BrowserTab from "@/components/browser-tab";
import { ThemeToggle } from "@/components/theme-toggle";

export default function Home() {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <main className="min-h-screen w-full flex flex-col">
          <div className="container py-4 md:py-8">
            <header className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  MCP Router
                </h1>
                <p className="text-muted-foreground">Model Context Protocol Router UI</p>
              </div>
              <div>
                <ThemeToggle />
              </div>
            </header>

            <Tabs defaultValue="query" className="w-full">
              <TabsList className="mb-4 w-full flex flex-wrap h-auto justify-start">
                <TabsTrigger value="query" className="rounded-md px-4 py-2">
                  Query
                </TabsTrigger>
                <TabsTrigger value="servers" className="rounded-md px-4 py-2">
                  Servers
                </TabsTrigger>
                <TabsTrigger value="models" className="rounded-md px-4 py-2">
                  Models
                </TabsTrigger>
                <TabsTrigger value="agents" className="rounded-md px-4 py-2">
                  Agents
                </TabsTrigger>
                <TabsTrigger value="tasks" className="rounded-md px-4 py-2">
                  Tasks
                </TabsTrigger>
                <TabsTrigger value="browser" className="rounded-md px-4 py-2">
                  Browser
                </TabsTrigger>
                <TabsTrigger value="mcp-modules" className="rounded-md px-4 py-2">
                  MCP Modules
                </TabsTrigger>
                <TabsTrigger value="settings" className="rounded-md px-4 py-2">
                  Settings
                </TabsTrigger>
              </TabsList>

              <TabsContent value="query">
                <QueryTab />
              </TabsContent>

              <TabsContent value="servers">
                <ServersTab />
              </TabsContent>

              <TabsContent value="models">
                <ModelsTab />
              </TabsContent>
              
              <TabsContent value="agents">
                <AgentsTab />
              </TabsContent>

              <TabsContent value="tasks">
                <TasksTab />
              </TabsContent>
              
              <TabsContent value="browser">
                <BrowserTab />
              </TabsContent>
              
              <TabsContent value="mcp-modules">
                <MCPModulesTab />
              </TabsContent>

              <TabsContent value="settings">
                <SettingsTab />
              </TabsContent>
            </Tabs>
          </div>
        </main>
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  );
} 