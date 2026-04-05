"use client";

import React from "react";
import { MessageCircle, Users } from "lucide-react";

interface SlackMessage {
  user: string;
  username?: string;
  ts: string;
  text: string;
  reactions?: string[];
}

interface SlackPanelProps {
  messages: SlackMessage[];
  participantCount: number;
  threadId?: string;
  loading?: boolean;
}

const SlackPanel: React.FC<SlackPanelProps> = ({
  messages,
  participantCount,
  threadId = "",
  loading = false,
}) => {
  const formatTime = (ts: string) => {
    try {
      // Slack timestamp format: "1234567890.123456"
      const unixTs = parseFloat(ts) * 1000;
      return new Date(unixTs).toLocaleTimeString();
    } catch {
      return "Unknown";
    }
  };

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6 flex flex-col h-full">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-3">
          <MessageCircle className="h-5 w-5 text-blue-400" />
          Slack Thread Messages
        </h2>

        {/* Participant Info */}
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Users className="h-4 w-4" />
          <span>{participantCount} participant(s)</span>
        </div>

        {threadId && (
          <div className="text-xs text-gray-500 mt-2">
            Thread ID: <span className="font-mono">{threadId}</span>
          </div>
        )}
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto space-y-3 bg-black/30 rounded p-3 border border-white/5">
        {loading ? (
          <div className="text-gray-500 text-center py-8">
            <div className="animate-spin inline-block mb-2">⌛</div>
            <div>Loading Slack messages...</div>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            No Slack messages found for this analysis.
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className="border-l-2 border-blue-500/30 pl-3 py-2">
              {/* User and timestamp */}
              <div className="flex items-baseline gap-2 mb-1">
                <span className="font-semibold text-blue-400 text-sm">
                  {msg.username || msg.user}
                </span>
                <span className="text-gray-500 text-xs">
                  {formatTime(msg.ts)}
                </span>
              </div>

              {/* Message text */}
              <div className="text-gray-300 text-sm break-words whitespace-pre-wrap">
                {msg.text}
              </div>

              {/* Reactions */}
              {msg.reactions && msg.reactions.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {msg.reactions.map((reaction, j) => (
                    <span
                      key={j}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs bg-gray-500/20 text-gray-300"
                    >
                      :{reaction}:
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Stats Footer */}
      <div className="mt-3 text-xs text-gray-500 text-right">
        {messages.length} message(s)
      </div>
    </div>
  );
};

export default SlackPanel;
