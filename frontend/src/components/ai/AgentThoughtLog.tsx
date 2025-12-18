'use client'

import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface AgentLog {
  timestamp: string;
  agent: string;
  message: string;
}

export function AgentThoughtLog() {
  const [logs, setLogs] = useState<AgentLog[]>([]);

  useEffect(() => {
    // Use relative path which will be proxied in dev or work in prod
    const eventSource = new EventSource('/api/v1/stream');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLogs((prev) => {
          const newLog = {
            timestamp: new Date().toISOString(),
            agent: data.source || 'System',
            message: typeof data.payload === 'string' ? data.payload : JSON.stringify(data.payload)
          };
          // Keep only last 100 logs to prevent memory issues
          const updatedLogs = [...prev, newLog];
          if (updatedLogs.length > 100) {
            return updatedLogs.slice(updatedLogs.length - 100);
          }
          return updatedLogs;
        });
      } catch (e) {
        console.error('Failed to parse SSE message', e);
      }
    };

    return () => eventSource.close();
  }, []);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Agent Thoughts</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-xs h-64 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={`${log.timestamp}-${i}`} className="mb-1">
              <span className="text-gray-500">[{log.timestamp.split('T')[1].split('.')[0]}]</span>{' '}
              <span className="text-blue-400">{log.agent}:</span>{' '}
              {log.message}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
