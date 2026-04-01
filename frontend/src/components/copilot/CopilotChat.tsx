import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { copilotApi, ChatMessage } from '../../api/copilot';
import { SendIcon } from 'lucide-react';

interface CopilotChatProps {
  noteId: string;
}

export function CopilotChat({ noteId }: CopilotChatProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const chatMutation = useMutation({
    mutationFn: ({ message, history }: { message: string; history: ChatMessage[] }) =>
      copilotApi.chat(noteId, message, history),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, data.message]);
    },
  });

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    // Capture current messages for history before async mutation
    const currentHistory = [...messages, userMessage];
    setMessages(currentHistory);
    chatMutation.mutate({ message: input, history: currentHistory });
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full p-4">
      {/* Messages */}
      <div className="flex-1 space-y-3 overflow-auto">
        {messages.length === 0 && (
          <p className="text-sm text-muted-foreground text-center mt-8">
            Ask questions about this note
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`rounded-lg p-3 text-sm ${
              msg.role === 'user'
                ? 'bg-muted ml-8'
                : 'bg-primary text-primary-foreground mr-8'
            }`}
          >
            {msg.content}
          </div>
        ))}
        {chatMutation.isPending && (
          <div className="bg-muted rounded-lg p-3 text-sm animate-pulse">
            Thinking...
          </div>
        )}
        {chatMutation.isError && (
          <div className="bg-destructive/10 text-destructive rounded-lg p-3 text-sm">
            Couldn't generate response. Try again.
          </div>
        )}
      </div>

      {/* Input */}
      <div className="mt-4 flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about this note..."
          className="flex-1 resize-none rounded border p-2 text-sm min-h-[60px]"
          rows={2}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || chatMutation.isPending}
          className="px-3 py-2 rounded bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 self-end"
        >
          <SendIcon className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
