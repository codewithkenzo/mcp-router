"use client";

import { useState } from "react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  Tabs, 
  TabsList, 
  TabsTrigger, 
  TabsContent 
} from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Separator } from "@/components/ui/separator";
import { Label } from "@/components/ui/label";
import { Save, AlertTriangle } from "lucide-react";
import MCPConnectionForm from "./mcp-connection-form";

interface GeneralSettings {
  autoSync: boolean;
  callTimeout: number;
  webPassword: string;
}

interface WebDAVSettings {
  url: string;
  username: string;
  password: string;
  baseDir: string;
}

export default function SettingsTab() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("general");
  
  // General settings
  const [generalSettings, setGeneralSettings] = useState<GeneralSettings>({
    autoSync: true,
    callTimeout: 30,
    webPassword: "",
  });
  
  // WebDAV settings
  const [webdavSettings, setWebdavSettings] = useState<WebDAVSettings>({
    url: "",
    username: "",
    password: "",
    baseDir: "mcp-router",
  });

  function onGeneralSubmit(e: React.FormEvent) {
    e.preventDefault();
    toast({
      title: "Settings updated",
      description: "Your general settings have been saved.",
    });
  }

  function onWebDAVSubmit(e: React.FormEvent) {
    e.preventDefault();
    toast({
      title: "WebDAV settings updated",
      description: "Your WebDAV settings have been saved.",
    });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Settings</CardTitle>
        <CardDescription>
          Configure your MCP Router settings
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="general" className="w-full" value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="connections">MCP Connections</TabsTrigger>
            <TabsTrigger value="webdav">WebDAV</TabsTrigger>
          </TabsList>
          <TabsContent value="general">
            <form onSubmit={onGeneralSubmit} className="space-y-6">
              <div className="flex flex-row items-center justify-between rounded-lg border p-4">
                <div className="space-y-0.5">
                  <Label className="text-base">Auto Sync</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically sync settings across devices
                  </p>
                </div>
                <Switch
                  checked={generalSettings.autoSync}
                  onCheckedChange={(value) => {
                    setGeneralSettings({ ...generalSettings, autoSync: value });
                  }}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="mcpTimeout">MCP Call Timeout (seconds)</Label>
                <Input 
                  id="mcpTimeout" 
                  type="number" 
                  min="1" 
                  value={generalSettings.callTimeout.toString()}
                  onChange={(e) => {
                    setGeneralSettings({ ...generalSettings, callTimeout: Number(e.target.value) });
                  }}
                />
                <p className="text-sm text-muted-foreground">
                  Maximum time to wait for MCP responses
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="webAccessPassword">Web Access Password</Label>
                <Input 
                  id="webAccessPassword" 
                  type="password"
                  value={generalSettings.webPassword}
                  onChange={(e) => {
                    setGeneralSettings({ ...generalSettings, webPassword: e.target.value });
                  }}
                />
                <p className="text-sm text-muted-foreground">
                  Password for accessing web interface
                </p>
              </div>
              
              <Button type="submit">
                <Save className="mr-2 h-4 w-4" />
                Save Settings
              </Button>
            </form>
          </TabsContent>
          <TabsContent value="connections">
            <MCPConnectionForm 
              onConnect={(connection) => {
                console.log("Connected to:", connection);
              }}
              onDisconnect={(connection) => {
                console.log("Disconnected from:", connection);
              }}
            />
          </TabsContent>
          <TabsContent value="webdav">
            <form onSubmit={onWebDAVSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="webdavUrl">WebDAV URL</Label>
                <Input 
                  id="webdavUrl" 
                  placeholder="https://example.com/webdav/"
                  value={webdavSettings.url}
                  onChange={(e) => {
                    setWebdavSettings({ ...webdavSettings, url: e.target.value });
                  }}
                />
                <p className="text-sm text-muted-foreground">
                  URL of your WebDAV server
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="webdavUsername">Username</Label>
                <Input 
                  id="webdavUsername"
                  value={webdavSettings.username}
                  onChange={(e) => {
                    setWebdavSettings({ ...webdavSettings, username: e.target.value });
                  }}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="webdavPassword">Password</Label>
                <Input 
                  id="webdavPassword" 
                  type="password"
                  value={webdavSettings.password}
                  onChange={(e) => {
                    setWebdavSettings({ ...webdavSettings, password: e.target.value });
                  }}
                />
              </div>
              
              <div className="bg-yellow-50 dark:bg-yellow-950 p-4 rounded-md flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                <div className="text-sm text-yellow-800 dark:text-yellow-300">
                  WebDAV settings are currently not functioning. This feature will be enabled in a future update.
                </div>
              </div>
              
              <Button type="submit">
                <Save className="mr-2 h-4 w-4" />
                Save WebDAV Settings
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
} 