"use client";

import { useState } from "react";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";
import { 
  PlusCircle, 
  Trash2, 
  Server, 
  RefreshCw, 
  Check,
  X 
} from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";

interface MCPConnection {
  id: string;
  name: string;
  url: string;
  isActive: boolean;
  isConnected?: boolean;
}

interface MCPConnectionFormProps {
  onConnect?: (connection: MCPConnection) => void;
  onDisconnect?: (connection: MCPConnection) => void;
}

export default function MCPConnectionForm({ onConnect, onDisconnect }: MCPConnectionFormProps) {
  const { toast } = useToast();
  const [connections, setConnections] = useState<MCPConnection[]>([
    {
      id: "local",
      name: "Local HyperChat",
      url: "http://localhost:16100/123456/",
      isActive: true,
      isConnected: false
    }
  ]);
  const [newConnectionName, setNewConnectionName] = useState("");
  const [newConnectionUrl, setNewConnectionUrl] = useState("");
  const [isTestingConnection, setIsTestingConnection] = useState<string | null>(null);

  const handleAddConnection = () => {
    if (!newConnectionName || !newConnectionUrl) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Connection name and URL are required"
      });
      return;
    }

    const newConnection: MCPConnection = {
      id: Date.now().toString(),
      name: newConnectionName,
      url: newConnectionUrl,
      isActive: false,
      isConnected: false
    };

    setConnections([...connections, newConnection]);
    setNewConnectionName("");
    setNewConnectionUrl("");

    toast({
      title: "Connection Added",
      description: `${newConnectionName} has been added to your connections`
    });
  };

  const handleRemoveConnection = (id: string) => {
    setConnections(connections.filter(conn => conn.id !== id));
    
    toast({
      title: "Connection Removed",
      description: "The connection has been removed"
    });
  };

  const handleToggleActive = (id: string) => {
    setConnections(connections.map(conn => 
      conn.id === id ? { ...conn, isActive: !conn.isActive } : conn
    ));
  };

  const handleTestConnection = async (connection: MCPConnection) => {
    setIsTestingConnection(connection.id);
    
    try {
      // In a real implementation, we would test the connection
      // For demo purposes, we'll simulate a successful connection after a delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setConnections(connections.map(conn => 
        conn.id === connection.id ? { ...conn, isConnected: true } : conn
      ));
      
      toast({
        title: "Connection Successful",
        description: `Successfully connected to ${connection.name}`,
      });
      
      if (onConnect) {
        onConnect(connection);
      }
    } catch (error) {
      setConnections(connections.map(conn => 
        conn.id === connection.id ? { ...conn, isConnected: false } : conn
      ));
      
      toast({
        variant: "destructive",
        title: "Connection Failed",
        description: `Failed to connect to ${connection.name}`,
      });
      
      if (onDisconnect) {
        onDisconnect(connection);
      }
    } finally {
      setIsTestingConnection(null);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">MCP Connections</h2>
      <p className="text-muted-foreground">
        Configure connections to MCP providers to discover and install modules
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {connections.map(connection => (
          <Card key={connection.id} className={connection.isActive ? "border-primary" : ""}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{connection.name}</CardTitle>
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id={`active-${connection.id}`}
                    checked={connection.isActive}
                    onCheckedChange={() => handleToggleActive(connection.id)}
                  />
                  <Label htmlFor={`active-${connection.id}`}>Active</Label>
                </div>
              </div>
              <CardDescription className="text-xs truncate">{connection.url}</CardDescription>
            </CardHeader>
            <CardFooter className="flex justify-between">
              <Button 
                variant="outline"
                size="sm"
                onClick={() => handleTestConnection(connection)}
                disabled={isTestingConnection === connection.id}
              >
                {isTestingConnection === connection.id ? (
                  <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                ) : connection.isConnected ? (
                  <Check className="h-4 w-4 mr-1 text-green-500" />
                ) : (
                  <Server className="h-4 w-4 mr-1" />
                )}
                {connection.isConnected ? "Connected" : "Test Connection"}
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => handleRemoveConnection(connection.id)}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
      
      <Separator className="my-6" />
      
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Add New Connection</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="connection-name">Connection Name</Label>
            <Input 
              id="connection-name" 
              placeholder="My MCP Provider"
              value={newConnectionName}
              onChange={e => setNewConnectionName(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="connection-url">Connection URL</Label>
            <Input 
              id="connection-url" 
              placeholder="http://example.com/mcp/"
              value={newConnectionUrl}
              onChange={e => setNewConnectionUrl(e.target.value)}
            />
          </div>
        </div>
        <Button onClick={handleAddConnection}>
          <PlusCircle className="h-4 w-4 mr-2" />
          Add Connection
        </Button>
      </div>
    </div>
  );
} 