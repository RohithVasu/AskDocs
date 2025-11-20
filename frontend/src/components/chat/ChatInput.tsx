import React from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Loader2, Square } from "lucide-react";

interface ChatInputProps {
    input: string;
    setInput: (value: string) => void;
    handleSend: () => void;
    isLoading: boolean;
    handleStop?: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
    input,
    setInput,
    handleSend,
    isLoading,
    handleStop,
}) => {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="max-w-4xl mx-auto p-4">
                <div className="flex gap-2">
                    <Textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask a question about your documents..."
                        className="min-h-[60px] max-h-[200px] resize-none"
                        disabled={isLoading}
                    />
                    {isLoading && handleStop ? (
                        <Button
                            onClick={handleStop}
                            variant="destructive"
                            size="icon"
                            className="self-end"
                        >
                            <Square className="h-5 w-5 fill-current" />
                        </Button>
                    ) : (
                        <Button
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading}
                            className="ai-gradient self-end"
                            size="icon"
                        >
                            {isLoading ? (
                                <Loader2 className="h-5 w-5 animate-spin" />
                            ) : (
                                <Send className="h-5 w-5" />
                            )}
                        </Button>
                    )}
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                    Press Enter to send, Shift + Enter for new line
                </p>
            </div>
        </div>
    );
};
