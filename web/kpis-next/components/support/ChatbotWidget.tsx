'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  escalation_needed?: boolean;
  suggested_actions?: string[];
}

interface ChatbotWidgetProps {
  customerEmail?: string;
  customerName?: string;
  onEscalation?: (message: string) => void;
  className?: string;
}

export default function ChatbotWidget({
  customerEmail,
  customerName,
  onEscalation,
  className = ''
}: ChatbotWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/support/chatbot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation_id: conversationId,
          customer_email: customerEmail,
          customer_name: customerName,
          conversation_history: messages.map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      });

      if (!response.ok) {
        throw new Error('Error al enviar mensaje');
      }

      const data = await response.json();

      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      const botMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        confidence: data.confidence,
        escalation_needed: data.escalation_needed,
        suggested_actions: data.suggested_actions
      };

      setMessages(prev => [...prev, botMessage]);

      // Si necesita escalación, notificar
      if (data.escalation_needed && onEscalation) {
        onEscalation(inputMessage);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo o contacta a soporte directamente.',
        timestamp: new Date(),
        escalation_needed: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestedAction = (action: string) => {
    if (action.toLowerCase().includes('agente') || action.toLowerCase().includes('soporte')) {
      // Crear ticket directamente
      if (onEscalation) {
        onEscalation(action);
      }
    } else {
      // Usar la acción como mensaje
      setInputMessage(action);
    }
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
      {/* Botón flotante */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-300 hover:scale-110"
          aria-label="Abrir chatbot"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {messages.length > 0 ? messages.length : '1'}
          </span>
        </button>
      )}

      {/* Widget de chat */}
      {isOpen && (
        <div className="bg-white rounded-lg shadow-2xl w-96 h-[600px] flex flex-col border border-gray-200">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <div>
              <h3 className="font-semibold">Soporte al Cliente</h3>
              <p className="text-xs opacity-90">Estamos aquí para ayudarte</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-gray-200 transition-colors"
              aria-label="Cerrar chatbot"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Mensajes */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <p className="mb-2">¡Hola! 👋</p>
                <p className="text-sm">¿En qué puedo ayudarte hoy?</p>
                <p className="text-xs mt-4 text-gray-400">
                  Puedo responder preguntas frecuentes o conectarte con un agente humano si lo necesitas.
                </p>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  {message.escalation_needed && (
                    <div className="mt-2 pt-2 border-t border-gray-300">
                      <p className="text-xs opacity-75">
                        ⚠️ Se necesita asistencia de un agente humano
                      </p>
                    </div>
                  )}
                  {message.suggested_actions && message.suggested_actions.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {message.suggested_actions.map((action, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSuggestedAction(action)}
                          className="block text-xs underline hover:no-underline opacity-75 hover:opacity-100"
                        >
                          {action}
                        </button>
                      ))}
                    </div>
                  )}
                  <p className="text-xs opacity-60 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu mensaje..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              Presiona Enter para enviar
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

