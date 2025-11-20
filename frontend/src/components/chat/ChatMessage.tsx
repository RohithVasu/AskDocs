import React from "react";
import { Card } from "@/components/ui/card";
import { User, Bot } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomOneDark } from "react-syntax-highlighter/dist/esm/styles/hljs";
import type { Message } from "@/types";

interface ChatMessageProps {
    message: Message;
    isTyping?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, isTyping }) => {
    const isUser = message.role === "user";

    return (
        <div className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
            {/* Assistant Icon */}
            {!isUser && (
                <div className="ai-gradient p-2 rounded-lg h-fit shrink-0">
                    <Bot className="h-5 w-5 text-white" />
                </div>
            )}

            {/* Message Content */}
            <Card
                className={`max-w-[85%] md:max-w-[75%] p-4 ${isUser ? "ai-gradient text-white border-none" : "bg-card"
                    }`}
            >
                <div className={isUser ? "" : "markdown-content"}>
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                        components={{
                            h1: (props: any) => (
                                <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />
                            ),
                            h2: (props: any) => (
                                <h2 className="text-xl font-semibold mt-3 mb-2" {...props} />
                            ),
                            h3: (props: any) => (
                                <h3 className="text-lg font-semibold mt-2 mb-1" {...props} />
                            ),
                            ul: (props: any) => (
                                <ul className="list-disc pl-6 space-y-1" {...props} />
                            ),
                            ol: (props: any) => (
                                <ol className="list-decimal pl-6 space-y-1" {...props} />
                            ),
                            blockquote: (props: any) => (
                                <blockquote
                                    className={`border-l-4 pl-3 italic ${isUser ? "border-white/50" : "border-primary text-muted-foreground"
                                        }`}
                                    {...props}
                                />
                            ),
                            code: ({
                                inline,
                                className,
                                children,
                                ...props
                            }: {
                                inline?: boolean;
                                className?: string;
                                children?: React.ReactNode;
                            }) => {
                                const match = /language-(\w+)/.exec(className || "");
                                if (!inline && match) {
                                    return (
                                        <SyntaxHighlighter
                                            language={match[1]}
                                            style={atomOneDark}
                                            PreTag="div"
                                            className="rounded-lg text-sm my-2"
                                            {...props}
                                        >
                                            {String(children).replace(/\n$/, "")}
                                        </SyntaxHighlighter>
                                    );
                                }
                                return (
                                    <code
                                        className={`${isUser
                                            ? "bg-white/20 text-white"
                                            : "bg-muted text-foreground"
                                            } px-1.5 py-0.5 rounded text-sm font-mono`}
                                        {...props}
                                    >
                                        {children}
                                    </code>
                                );
                            },
                            p: (props: any) => (
                                <p
                                    className="leading-relaxed text-sm mb-2 last:mb-0 whitespace-pre-wrap"
                                    {...props}
                                />
                            ),
                            a: (props: any) => (
                                <a
                                    className={`underline underline-offset-2 ${isUser ? "text-white hover:text-white/80" : "text-primary hover:text-primary/80"
                                        }`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    {...props}
                                />
                            ),
                        }}
                    >
                        {message.content}
                    </ReactMarkdown>
                    {isTyping && (
                        <span className="inline-block w-2 h-4 ml-1 bg-primary align-middle animate-pulse" />
                    )}
                </div>
            </Card>

            {/* User Icon */}
            {isUser && (
                <div className="bg-primary p-2 rounded-lg h-fit shrink-0">
                    <User className="h-5 w-5 text-white" />
                </div>
            )}
        </div>
    );
};
