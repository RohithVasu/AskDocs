import { create } from 'zustand';
import { ChatSession, Message } from '@/types';
import api from '@/lib/api';

interface ChatState {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  messages: Message[];
  setSessions: (sessions: ChatSession[]) => void;
  setCurrentSession: (session: ChatSession | null) => void;
  setMessages: (
    updater: Message[] | ((prev: Message[]) => Message[])
  ) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, newContent: string) => void;
  loadSessions: () => Promise<void>;
}

export const useChatStore = create<ChatState>((set) => ({
  sessions: [],
  currentSession: null,
  messages: [],

  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (session) => set({ currentSession: session }),

  // ✅ smarter setter: supports both array or function
  setMessages: (updater) =>
    set((state) => ({
      messages:
        typeof updater === 'function' ? updater(state.messages) : updater,
    })),

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  updateMessage: (id, newContent) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content: newContent } : msg
      ),
    })),

  loadSessions: async () => {
    try {
      const response = await api.get('/sessions/');
      set({ sessions: response.data.data || [] });
    } catch {
      set({ sessions: [] });
    }
  },
}));
