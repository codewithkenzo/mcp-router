'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

interface TaskContextType {
  taskIds: string[];
  addTask: (id: string) => void;
  // We might add functions to remove tasks later if needed
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

export const TaskProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [taskIds, setTaskIds] = useState<string[]>([]);

  const addTask = useCallback((id: string) => {
    setTaskIds((prevIds) => {
      // Add the new ID only if it doesn't already exist, placing newest first
      if (!prevIds.includes(id)) {
        return [id, ...prevIds];
      } 
      return prevIds;
    });
  }, []);

  return (
    <TaskContext.Provider value={{ taskIds, addTask }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = (): TaskContextType => {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTasks must be used within a TaskProvider');
  }
  return context;
}; 