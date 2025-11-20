// import { useLayoutEffect, useEffect, useState, useRef } from 'react';
// import { motion, AnimatePresence } from "framer-motion";
// import { useParams } from 'react-router-dom';
// import { Button } from '@/components/ui/button';
// import { Textarea } from '@/components/ui/textarea';
// import { Card } from '@/components/ui/card';
// import { ScrollArea } from '@/components/ui/scroll-area';
// import { Send, Loader2, Sparkles, User } from 'lucide-react';
// import { useChatStore } from '@/stores/chatStore';
// import api from '@/lib/api';
// import { toast } from 'sonner';
// import { Message } from '@/types';
// import ReactMarkdown from 'react-markdown';
// import remarkGfm from 'remark-gfm';
// import rehypeHighlight from 'rehype-highlight';
// import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';


// export default function Chat() {
//   const { sessionId } = useParams();
//   const { messages, setMessages, addMessage, updateMessage, setCurrentSession, loadSessions } = useChatStore();
//   const [input, setInput] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [page, setPage] = useState(1);
//   const [hasMore, setHasMore] = useState(true);
//   const firstLoad = useRef(true);
//   const scrollContainerRef = useRef<HTMLDivElement | null>(null);
//   const bottomRef = useRef<HTMLDivElement | null>(null);

//   useEffect(() => {
//     if (!sessionId) return;

//     // 🧹 Clear old messages instantly to avoid flicker
//     setMessages([]);

//     firstLoad.current = true;
//     loadSession();

//     // ✅ Load and instantly scroll to bottom
//     loadMessages(1, { scrollToBottom: true });
//   }, [sessionId]);

//   useLayoutEffect(() => {
//     if (firstLoad.current && messages.length > 0 && scrollContainerRef.current) {
//       const el = scrollContainerRef.current;
//       el.scrollTop = el.scrollHeight;
//       firstLoad.current = false;
//     }
//   }, [messages.length]);

//   const loadSession = async () => {
//     try {
//       const response = await api.get(`/sessions/${sessionId}`);
//       setCurrentSession(response.data);
//     } catch {
//       toast.error('Failed to load session');
//     }
//   };

//   const loadMessages = async (pageNum = 1, options: { scrollToBottom?: boolean } = {}) => {
//     try {
//       const response = await api.get(`/sessions/${sessionId}/messages`, {
//         params: { page: pageNum, page_size: 20 },
//       });

//       const { data, meta } = response.data;

//       if (pageNum === 1) {
//         // 🟢 First page = latest messages
//         setMessages(data);

//         if (options.scrollToBottom) {
//           requestAnimationFrame(() => {
//             const el = scrollContainerRef.current;
//             if (el) el.scrollTop = el.scrollHeight; // scroll to latest
//           });
//         }
//       } else {
//         // 🟡 Prepend older messages
//         const container = scrollContainerRef.current;
//         const oldScrollHeight = container?.scrollHeight || 0;
//         setMessages([...data, ...messages]);
//         setTimeout(() => {
//           if (container) {
//             const newScrollHeight = container.scrollHeight;
//             container.scrollTop = newScrollHeight - oldScrollHeight;
//           }
//         }, 50);
//       }

//       // 🔢 Detect if more messages remain
//       setHasMore(meta?.has_next_page ?? false);
//       setPage(pageNum);
//     } catch {
//       toast.error('Failed to load messages');
//     }
//   };

//   const handleScroll = () => {
//     const container = scrollContainerRef.current;
//     if (!container || isLoading || !hasMore) return;

//     // ✅ Detect when user scrolls near top to load older messages
//     if (container.scrollTop < 100) {
//       loadMessages(page + 1);
//     }
//   };

//   const handleSend = async () => {
//     if (!input.trim() || !sessionId || isLoading) return;

//     const userMessage: Message = {
//       id: Date.now().toString(),
//       session_id: sessionId,
//       role: 'user',
//       content: input.trim(),
//       created_at: new Date().toISOString(),
//     };

//     addMessage(userMessage);
//     setInput('');
//     setIsLoading(true);

//     // ✅ Immediately scroll to bottom after sending
//     setTimeout(() => {
//       bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
//     }, 50);

//     try {
//       const response = await api.post('/chat/', {
//         session_id: sessionId,
//         query: input.trim(),
//       });

//       const fullResponse = response.data?.data?.response || 'No response received.';
//       const assistantMessageId = (Date.now() + 1).toString();

//       const assistantMessage: Message = {
//         id: assistantMessageId,
//         session_id: sessionId,
//         role: 'assistant',
//         content: '',
//         created_at: new Date().toISOString(),
//       };

//       addMessage(assistantMessage);

//       let index = 0;
//       const typingSpeed = 10;
//       const interval = setInterval(() => {
//         index++;
//         updateMessage(assistantMessageId, fullResponse.slice(0, index));

//         // ✅ Smart scroll only if user hasn’t scrolled up
//         const container = scrollContainerRef.current;
//         if (container) {
//           const isNearBottom =
//             container.scrollHeight - container.scrollTop - container.clientHeight < 200;
//           if (isNearBottom) {
//             bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
//           }
//         }

//         if (index >= fullResponse.length) {
//           clearInterval(interval);
//           setTimeout(() => {
//             loadSessions();
//             bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
//           }, 500);
//         }
//       }, typingSpeed);

//     } catch (error: any) {
//       toast.error(error.response?.data?.detail || 'Failed to send message');
//     } finally {
//       setIsLoading(false);
//     }
//   };


//   const handleKeyDown = (e: React.KeyboardEvent) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSend();
//     }
//   };

//   return (
//     <div className="flex flex-col h-full">
//       {/* Chat Messages */}
//       <ScrollArea className="flex-1 p-6" viewportRef={scrollContainerRef} onScrollCapture={handleScroll}>
//         <motion.div
//           style={{ overflowAnchor: "none" }}
//           className="max-w-4xl mx-auto space-y-6"
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           transition={{ duration: 0.3 }}
//         >
//           <div className="max-w-4xl mx-auto space-y-6">
//             {/* Empty chat placeholder */}
//             {messages.length === 0 && !isLoading && (
//               <motion.div
//                 initial={{ opacity: 0, y: 10 }}
//                 animate={{ opacity: 1, y: 0 }}
//                 className="flex flex-col items-center justify-center text-center py-24 relative"
//               >
//                 {/* Floating chat bubbles */}
//                 <div className="relative p-6 rounded-full mb-4 bg-primary/10 flex items-center justify-center overflow-visible">
//                   {/* Central chat icon */}
//                   <div className="bg-primary p-4 rounded-full shadow-md text-white">
//                     <svg
//                       xmlns="http://www.w3.org/2000/svg"
//                       className="h-8 w-8"
//                       fill="none"
//                       viewBox="0 0 24 24"
//                       stroke="currentColor"
//                       strokeWidth="1.5"
//                     >
//                       <path
//                         strokeLinecap="round"
//                         strokeLinejoin="round"
//                         d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.77 9.77 0 01-3-.47L4 20l1.09-3.27A8.962 8.962 0 013 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
//                       />
//                     </svg>
//                   </div>

//                   {/* Floating bubbles around */}
//                   <motion.div
//                     className="absolute -top-6 -right-4 text-primary/70"
//                     animate={{ y: [0, -6, 0], opacity: [0.8, 1, 0.8] }}
//                     transition={{ duration: 2, repeat: Infinity, delay: 0 }}
//                   >
//                     💬
//                   </motion.div>

//                   <motion.div
//                     className="absolute -bottom-4 -left-5 text-primary/60"
//                     animate={{ y: [0, -8, 0], opacity: [0.8, 1, 0.8] }}
//                     transition={{ duration: 2.5, repeat: Infinity, delay: 0.4 }}
//                   >
//                     💭
//                   </motion.div>
//                 </div>

//                 <h2 className="text-xl font-semibold mb-2">Start a new conversation</h2>
//                 <p className="text-muted-foreground max-w-md text-sm">
//                   Ask any question about your uploaded documents and I’ll help you find the
//                   most relevant answers.
//                 </p>
//               </motion.div>
//             )}

//             {/* Loading conversation */}
//             {messages.length === 0 && isLoading && (
//               <div className="text-center text-sm text-muted-foreground py-10">
//                 Loading conversation...
//               </div>
//             )}

//             {/* Render all messages */}
//             {messages.map((message) => (
//               <div
//                 key={message.id}
//                 className={`flex gap-4 ${
//                   message.role === 'user' ? 'justify-end' : 'justify-start'
//                 }`}
//               >
//                 {message.role === 'assistant' && (
//                   <div className="ai-gradient p-2 rounded-lg h-fit">
//                     <Sparkles className="h-5 w-5 text-white" />
//                   </div>
//                 )}

//                 <Card
//                   className={`max-w-[70%] p-4 ${
//                     message.role === 'user' ? 'ai-gradient text-white' : 'bg-card'
//                   }`}
//                 >
//                   <ReactMarkdown
//                     remarkPlugins={[remarkGfm]}
//                     rehypePlugins={[rehypeHighlight]}
//                     // className="prose max-w-none prose-invert"
//                     components={{
//                       h1: ({ node, ...props }) => (
//                         <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />
//                       ),
//                       h2: ({ node, ...props }) => (
//                         <h2 className="text-xl font-semibold mt-3 mb-2" {...props} />
//                       ),
//                       h3: ({ node, ...props }) => (
//                         <h3 className="text-lg font-semibold mt-2 mb-1" {...props} />
//                       ),
//                       ul: ({ node, ...props }) => (
//                         <ul className="list-disc pl-6 space-y-1" {...props} />
//                       ),
//                       ol: ({ node, ...props }) => (
//                         <ol className="list-decimal pl-6 space-y-1" {...props} />
//                       ),
//                       blockquote: ({ node, ...props }) => (
//                         <blockquote
//                           className="border-l-4 border-primary pl-3 italic text-muted-foreground"
//                           {...props}
//                         />
//                       ),
//                       code({
//                         node,
//                         inline,
//                         className,
//                         children,
//                         ...props
//                       }: {
//                         node?: any;
//                         inline?: boolean;
//                         className?: string;
//                         children?: React.ReactNode;
//                         [key: string]: any;
//                       }) {
//                         const match = /language-(\w+)/.exec(className || '');
//                         return !inline ? (
//                           <SyntaxHighlighter
//                             language={match ? match[1] : 'plaintext'}
//                             style={atomOneDark}
//                             PreTag="div"
//                             className="rounded-lg text-sm my-2"
//                             {...props}
//                           >
//                             {String(children).replace(/\n$/, '')}
//                           </SyntaxHighlighter>
//                         ) : (
//                           <code
//                             className="bg-muted text-sm px-1 py-0.5 rounded"
//                             {...props}
//                           >
//                             {children}
//                           </code>
//                         );
//                       },
//                       p: ({ node, ...props }) => (
//                         <p
//                           className="leading-relaxed text-sm mb-2 whitespace-pre-wrap"
//                           {...props}
//                         />
//                       ),
//                     }}
//                   >
//                     {message.content}
//                   </ReactMarkdown>
//                 </Card>

//                 {message.role === 'user' && (
//                   <div className="bg-primary p-2 rounded-lg h-fit">
//                     <User className="h-5 w-5 text-white" />
//                   </div>
//                 )}
//               </div>
//             ))}

//             {/* Loading animation */}
//             {isLoading && (
//               <motion.div className="flex gap-4">
//                 <div className="ai-gradient p-2 rounded-lg h-fit">
//                   <Sparkles className="h-5 w-5 text-white animate-pulse" />
//                 </div>
//                 <Card className="max-w-[70%] p-4">
//                   <motion.div
//                     animate={{ opacity: [0.5, 1, 0.5] }}
//                     transition={{ duration: 1.2, repeat: Infinity }}
//                     className="flex items-center gap-2"
//                   >
//                     <Loader2 className="h-4 w-4 animate-spin" />
//                     <span className="text-sm text-muted-foreground">
//                       Thinking...
//                     </span>
//                   </motion.div>
//                 </Card>
//               </motion.div>
//             )}
//           </div>
//           <div ref={bottomRef} />
//         </motion.div>
//       </ScrollArea>

//       {/* Input Area */}
//       <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
//         <div className="max-w-4xl mx-auto p-4">
//           <div className="flex gap-2">
//             <Textarea
//               value={input}
//               onChange={(e) => setInput(e.target.value)}
//               onKeyDown={handleKeyDown}
//               placeholder="Ask a question about your documents..."
//               className="min-h-[60px] max-h-[200px] resize-none"
//               disabled={isLoading}
//             />
//             <Button
//               onClick={handleSend}
//               disabled={!input.trim() || isLoading}
//               className="ai-gradient self-end"
//               size="icon"
//             >
//               {isLoading ? (
//                 <Loader2 className="h-5 w-5 animate-spin" />
//               ) : (
//                 <Send className="h-5 w-5" />
//               )}
//             </Button>
//           </div>
//           <p className="text-xs text-muted-foreground mt-2 text-center">
//             Press Enter to send, Shift + Enter for new line
//           </p>
//         </div>
//       </div>
//     </div>
//   );
// }





// Chat.tsx
import React, { useEffect, useLayoutEffect, useRef, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { User, Bot, Send, Loader2, ArrowDownCircle, Square } from "lucide-react";
import { useChatStore } from "@/stores/chatStore";
import api from "@/lib/api";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomOneDark } from "react-syntax-highlighter/dist/esm/styles/hljs";
import type { Message } from "@/types";

/**
 * Chat component features (per your spec):
 * - page=1 => newest messages
 * - uses existing useChatStore and api
 * - loads older messages on scroll up with loader at top
 * - preserve scroll position when prepending
 * - render markdown + code highlighting
 * - simulate typing of full response (backend returns full string)
 * - auto-scroll while typing unless user scrolled up (pause)
 * - jump-to-latest floating button
 */

const PAGE_SIZE = 20;
const TOP_LOAD_THRESHOLD = 120; // px from top to trigger older load
const NEAR_BOTTOM_THRESHOLD = 200; // px from bottom considered "near bottom"
const TYPING_INTERVAL_MS = 5; // lower => faster "typing" effect

export default function Chat(): JSX.Element {
  const { sessionId } = useParams<{ sessionId: string }>();
  const {
    messages,
    setMessages,
    addMessage,
    updateMessage,
    setCurrentSession,
    loadSessions,
  } = useChatStore();

  const scrollRef = useRef<HTMLDivElement | null>(null);
  const bottomAnchorRef = useRef<HTMLDivElement | null>(null);

  const scrollContainerRef = useRef<HTMLDivElement | null>(null);

  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [loadingOlder, setLoadingOlder] = useState<boolean>(false);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [input, setInput] = useState<string>("");
  const [isUserNearBottom, setIsUserNearBottom] = useState<boolean>(true);
  const [isTyping, setIsTyping] = useState<boolean>(false);


  // Used to avoid automatic scroll on initial render before messages present
  const initialOpenRef = useRef<boolean>(true);

  // -- LOAD SESSION METADATA --
  useEffect(() => {
    if (!sessionId) return;
    const loadSession = async () => {
      try {
        const r = await api.get(`/sessions/${sessionId}`);
        setCurrentSession(r.data);
      } catch (err) {
        toast.error("Failed to load session");
      }
    };
    loadSession();
  }, [sessionId, setCurrentSession]);

  // -- MESSAGES: initial load (page 1 = newest) --
  useEffect(() => {
    if (!sessionId) return;

    // Clear old messages first to avoid flicker from previous session
    setMessages([]);
    setPage(1);
    setHasMore(false);
    initialOpenRef.current = true;

    const loadLatest = async () => {
      try {
        const resp = await api.get(`/sessions/${sessionId}/messages`, {
          params: { page: 1, page_size: PAGE_SIZE },
        });
        const { data, meta } = resp.data;
        setMessages(data);
        setHasMore(Boolean(meta?.has_next_page));
        setPage(1);
        // soon after messages set, jump to bottom
        requestAnimationFrame(() => {
          scrollToBottomInstant();
          initialOpenRef.current = false;
        });
      } catch (err) {
        toast.error("Failed to load messages");
      }
    };

    loadLatest();
  }, [sessionId, setMessages]);

  // Ensure on first messages populate we jump to bottom (synchronous-ish)
  useLayoutEffect(() => {
    if (initialOpenRef.current && messages.length > 0) {
      // If scrollRef exists try set scroll to bottom immediately
      const el = scrollRef.current;
      if (el) el.scrollTop = el.scrollHeight;
      initialOpenRef.current = false;
    }
  }, [messages.length]);

  // -- Scroll helpers --
  const scrollToBottomSmooth = () => {
    bottomAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToBottomInstant = () => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
    else bottomAnchorRef.current?.scrollIntoView({ behavior: "auto" });
  };

  // -- Load older messages (page 2,3...) when user scrolls near top --
  const loadOlder = useCallback(
    async (nextPage: number) => {
      if (!sessionId || loadingOlder || !hasMore) return;
      setLoadingOlder(true);
      const container = scrollRef.current;
      const prevScrollHeight = container?.scrollHeight ?? 0;

      try {
        const resp = await api.get(`/sessions/${sessionId}/messages`, {
          params: { page: nextPage, page_size: PAGE_SIZE },
        });
        const { data, meta } = resp.data;

        // Prepend older messages while preserving viewport
        setMessages((prev) => {
          const merged = [...data, ...prev];
          return merged;
        });

        // After DOM update, adjust scrollTop so content doesn't jump
        // Use a small timeout to wait for rendering (works reliably)
        setTimeout(() => {
          const newScrollHeight = container?.scrollHeight ?? 0;
          if (container) {
            // Keep the top-most visible message stable:
            container.scrollTop = newScrollHeight - prevScrollHeight;
          }
        }, 50);

        setHasMore(Boolean(meta?.has_next_page));
        setPage(nextPage);
      } catch (err) {
        toast.error("Failed to load older messages");
      } finally {
        setLoadingOlder(false);
      }
    },
    [sessionId, hasMore, loadingOlder, setMessages]
  );

  // -- Scroll event handler --
  const onScroll = (e?: React.UIEvent) => {
    const container = scrollRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;

    // Detect near-top for older load
    if (scrollTop < TOP_LOAD_THRESHOLD && !loadingOlder && hasMore) {
      loadOlder(page + 1);
    }

    // Detect near-bottom for auto-scroll behavior & Jump-to-latest button visibility
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    const nearBottom = distanceFromBottom < NEAR_BOTTOM_THRESHOLD;
    setIsUserNearBottom(nearBottom);
  };

  const abortControllerRef = useRef<AbortController | null>(null);

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsSending(false);
      setIsTyping(false);
    }
  };

  // -- SEND MESSAGE (user query) --
  const handleSend = async () => {
    if (!sessionId || !input.trim() || isSending) return;
    const text = input.trim();
    setInput("");
    setIsSending(true);
    setIsTyping(true);

    // user message (optimistic)
    const userMsg: Message = {
      id: Date.now().toString(),
      session_id: sessionId,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    addMessage(userMsg);

    // Immediately scroll to bottom so user sees their message
    setTimeout(() => scrollToBottomSmooth(), 30);

    // assistant message placeholder
    const assistantId = (Date.now() + 1).toString();
    const assistantMsg: Message = {
      id: assistantId,
      session_id: sessionId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };
    addMessage(assistantMsg);

    abortControllerRef.current = new AbortController();

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${import.meta.env.VITE_BASE_API_URL}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          query: text,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) throw new Error("Failed to send message");
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        fullText += chunk;
        updateMessage(assistantId, fullText);

        if (isUserNearBottom) {
          bottomAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
        }
      }

    } catch (err: any) {
      if (err.name === 'AbortError') {
        // User stopped the request
        updateMessage(assistantId, "*Response stopped by user*");
      } else {
        // Display user-friendly error message in chat
        const errorMessage = "I'm sorry, I encountered an error while processing your request. Please try again. If the problem persists, check your internet connection or contact support.";
        updateMessage(assistantId, errorMessage);

        // Also show a toast for immediate feedback
        toast.error("Unable to get response. Please try again.");
      }
    } finally {
      setIsSending(false);
      setIsTyping(false);
      abortControllerRef.current = null;
      loadSessions();
    }
  };

  // handle enter key submit
  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Jump-to-latest button click
  const handleJumpToLatest = () => {
    scrollToBottomSmooth();
    setIsUserNearBottom(true);
  };

  // When user manually scrolls while assistant typing, they may pause auto-scrolling.
  // We already set isUserNearBottom in onScroll; no extra wiring needed.

  // -- Render helpers for markdown --
  const markdownComponents = {
    h1: (props: any) => <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />,
    h2: (props: any) => <h2 className="text-xl font-semibold mt-3 mb-2" {...props} />,
    h3: (props: any) => <h3 className="text-lg font-semibold mt-2 mb-1" {...props} />,
    ul: (props: any) => <ul className="list-disc pl-6 space-y-1" {...props} />,
    ol: (props: any) => <ol className="list-decimal pl-6 space-y-1" {...props} />,
    blockquote: (props: any) => (
      <blockquote className="border-l-4 border-primary pl-3 italic text-muted-foreground" {...props} />
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
      // Only render as code block if it has a language class (i.e., proper markdown code fence)
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
      // For inline code or code blocks without language, use subtle styling
      if (!inline) {
        return (
          <pre className="bg-transparent border border-border/50 p-3 rounded-lg text-sm my-2 overflow-x-auto whitespace-pre-wrap break-words">
            <code className="text-foreground font-mono" {...props}>{children}</code>
          </pre>
        );
      }
      // Inline code - render as normal text without any special styling
      return (
        <span className="text-foreground" {...props}>
          {children}
        </span>
      );
    },
    p: (props: any) => (
      <p className="leading-relaxed text-sm mb-2 whitespace-pre-wrap" {...props} />
    ),
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1">
        <ScrollArea
          className="h-full p-6"
          onScrollCapture={onScroll}
        >
          <div ref={scrollContainerRef}>
            <motion.div
              className="max-w-4xl mx-auto space-y-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.18 }}
              style={{ overflowAnchor: "none" }}
            >
              {/* Top loader when fetching older messages */}
              {loadingOlder && (
                <div className="flex justify-center py-2">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-muted/10 text-sm">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading older messages...
                  </div>
                </div>
              )}

              {/* Empty placeholder */}
              {messages.length === 0 && !isTyping && !isSending && (
                <div className="text-center py-24">
                  <div className="mb-4 text-4xl">💬</div>
                  <h2 className="text-xl font-semibold">Start a new conversation</h2>
                  <p className="text-sm text-muted-foreground max-w-md mx-auto mt-2">
                    Ask any question about your uploaded documents and I’ll help you find the most relevant answers.
                  </p>
                </div>
              )}

              {/* Render messages */}
              {messages.map((m) => {
                const isUser = m.role === "user";
                return (
                  <div key={m.id} className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
                    {/* Avatar for assistant */}
                    {!isUser && (
                      <div className="flex-shrink-0">
                        <div className="ai-gradient p-1.5 rounded-full h-fit">
                          <Bot className="h-4 w-4 text-white" />
                        </div>
                      </div>
                    )}

                    {/* Message content */}
                    <div
                      className={`max-w-[75%] px-4 py-3 rounded-2xl ${isUser
                        ? "ai-gradient text-white"
                        : "bg-muted/50"
                        }`}
                    >
                      <div className={isUser ? "" : "markdown-content"}>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeHighlight]}
                          skipHtml={true}
                          components={markdownComponents as any}
                        >
                          {m.content}
                        </ReactMarkdown>
                        {/* Show typing cursor if this is the last assistant message and still streaming */}
                        {!isUser &&
                          isTyping &&
                          messages[messages.length - 1]?.id === m.id && (
                            <span className="typing-cursor">▊</span>
                          )}
                      </div>
                    </div>

                    {/* Avatar for user */}
                    {isUser && (
                      <div className="flex-shrink-0">
                        <div className="bg-primary p-1.5 rounded-full h-fit">
                          <User className="h-4 w-4 text-white" />
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Typing indicator (if assistant being typed) */}
              {isSending && !isTyping && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="ai-gradient p-1.5 rounded-full h-fit">
                      <Loader2 className="h-4 w-4 animate-spin text-white" />
                    </div>
                  </div>
                  <div className="max-w-[75%] px-4 py-3 rounded-2xl bg-muted/50">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-pulse" />
                      <span className="text-sm text-muted-foreground">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={bottomAnchorRef} />
            </motion.div>
          </div>
        </ScrollArea>
      </div>

      {/* Input area */}
      <div className="sticky bottom-0 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-4xl mx-auto p-4">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask a question about your documents..."
              className="min-h-[60px] max-h-[200px] resize-none"
              disabled={isSending}
            />
            <Button
              onClick={isSending ? handleStop : handleSend}
              disabled={(!input.trim() && !isSending)}
              className="ai-gradient self-end"
              size="icon"
            >
              {isSending ? <Square className="h-5 w-5 fill-current" /> : <Send className="h-5 w-5" />}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Press Enter to send, Shift + Enter for new line
          </p>
        </div>
      </div>

      {/* Jump to latest floating button */}
      {!isUserNearBottom && (
        <div className="fixed right-6 bottom-24 z-50">
          <motion.div
            initial={{ y: 12, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.18 }}
          >
            <Button onClick={handleJumpToLatest} className="rounded-full px-3 py-2 shadow-lg">
              <ArrowDownCircle className="h-5 w-5 mr-2" />
              Latest
            </Button>
          </motion.div>
        </div>
      )}
    </div>
  );
}
