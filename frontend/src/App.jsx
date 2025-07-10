import { useState, useRef, useEffect } from "react";
import axios from "axios";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const welcomeMessage = {
      type: "bot",
      text: "👋 Hello! I'm your Walmart shopping assistant.\n\nI can help you:\n• Compare products\n• Find deals\n• Answer questions\n\nHow can I help you today?",
      products: [],
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { type: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      console.log("VITE_API_URL:", import.meta.env.VITE_API_URL);
      console.log("Sending:", { message: input, session_id: sessionId ?? "" });
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/chat`, {
        message: input,
        session_id: sessionId ?? "",
      });

      // Update session ID if received
      if (res.data.session_id) {
        setSessionId(res.data.session_id);
      }

      // Create bot message with both text and products
      const botMessage = {
        type: "bot",
        text: res.data.response,
        products: res.data.products || [],
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "❌ Sorry, I encountered an error. Please try again.",
          products: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setSessionId(null);
    setMessages([
      {
        type: "bot",
        text: "👋 Hello! I'm your Walmart shopping assistant.\n\nI can help you:\n• Compare products\n• Find deals\n• Track orders\n• Answer questions\n\nHow can I help you today?",
        products: [],
      },
    ]);
  };

  // Product card component
  const ProductCard = ({ product }) => {
    const rating = parseFloat(product.rating) || 0;

    return (
      <div className="mb-3 p-4 bg-blue-50 rounded-xl border border-blue-100 text-left shadow-sm transition-all hover:shadow-md">
        <div className="font-bold text-lg text-blue-900">{product.title}</div>

        <div className="text-gray-700">💲 {product.price}</div>

        {product.rating && (
          <div className="flex items-center py-1">
            <div className="flex">
              {[...Array(5)].map((_, idx) => (
                <svg
                  key={idx}
                  xmlns="http://www.w3.org/2000/svg"
                  className={`h-4 w-4 ${
                    idx < rating ? "text-yellow-400" : "text-gray-300"
                  }`}
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span className="ml-1 text-sm text-gray-600">
              {rating.toFixed(1)}/5.0
            </span>
          </div>
        )}

        <a
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center mt-2 px-4 py-2 bg-blue-600 text-white rounded-full text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4 mr-1"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
            <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
          </svg>
          View Product on Walmart
        </a>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans flex flex-col">
      {/* Walmart-themed header */}
      <header className="bg-blue-600 text-white shadow-md">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center">
            <div className="flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 mr-2"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M24 12c0 6.627-5.373 12-12 12S0 18.627 0 12 5.373 0 12 0s12 5.373 12 12z"
                  fill="#0071CE"
                />
                <path d="M12 20a8 8 0 100-16 8 8 0 000 16z" fill="#FFF" />
                <path d="M12 6a6 6 0 110 12 6 6 0 010-12z" fill="#0071CE" />
                <path d="M12 16a4 4 0 100-8 4 4 0 000 8z" fill="#FFC220" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold">Walmart Assistant</h1>
              <p className="text-xs opacity-80">
                Your personal shopping helper
              </p>
            </div>
          </div>
          <button
            onClick={clearChat}
            className="flex items-center text-sm bg-blue-700 hover:bg-blue-800 px-3 py-1.5 rounded-full transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                clipRule="evenodd"
              />
            </svg>
            New Chat
          </button>
        </div>
      </header>

      <main className="flex-1 px-4 py-6 max-w-4xl mx-auto w-full">
        <div className="bg-white shadow-xl rounded-xl overflow-hidden">
          {/* Chat container */}
          <div
            className="h-[65vh] overflow-y-auto p-4 bg-gradient-to-b from-blue-50 to-white space-y-4"
            style={{ scrollbarWidth: "thin" }}
          >
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-[90%] ${
                  msg.type === "user" ? "ml-auto" : "mr-auto"
                }`}
              >
                {msg.type === "bot" ? (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 text-blue-600"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="whitespace-pre-line">{msg.text}</div>
                      {msg.products && msg.products.length > 0 && (
                        <div className="mt-4 space-y-3">
                          {msg.products.map((product, i) => (
                            <ProductCard key={i} product={product} />
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start justify-end space-x-3">
                    <div className="flex-1 max-w-[85%]">
                      <div className="bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-tr-none">
                        {msg.text}
                      </div>
                    </div>
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 text-white"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 005 10a6 6 0 0012 0c0-.35-.03-.687-.086-1.016A5 5 0 0010 11z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-blue-600"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="flex space-x-1 py-2">
                  <div
                    className="h-2 w-2 bg-blue-600 rounded-full animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  ></div>
                  <div
                    className="h-2 w-2 bg-blue-600 rounded-full animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  ></div>
                  <div
                    className="h-2 w-2 bg-blue-600 rounded-full animate-bounce"
                    style={{ animationDelay: "600ms" }}
                  ></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="p-4 border-t">
            <div className="flex items-center gap-2">
              <input
                type="text"
                className="flex-1 border-2 border-gray-200 rounded-full px-4 py-3 focus:outline-none focus:border-blue-500 transition-colors"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask something like 'Compare Logitech and Razer mice'"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
                  loading || !input.trim()
                    ? "bg-gray-300"
                    : "bg-blue-600 hover:bg-blue-700"
                } text-white transition-colors`}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
            <p className="text-xs text-center text-gray-500 mt-2">
              Walmart Assistant can make mistakes. Verify important information.
            </p>
          </div>
        </div>

        {/* Quick suggestions */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            onClick={() => setInput("Show me deals on laptops under $500")}
            className="bg-white border border-gray-200 rounded-xl p-3 text-left hover:bg-blue-50 hover:border-blue-200 transition-colors"
          >
            <div className="font-medium text-blue-800">💻 Laptop Deals</div>
            <div className="text-xs text-gray-600 mt-1">
              Find discounted laptops
            </div>
          </button>
          <button
            onClick={() => setInput("Show Shirts")}
            className="bg-white border border-gray-200 rounded-xl p-3 text-left hover:bg-blue-50 hover:border-blue-200 transition-colors"
          >
            <div className="font-medium text-blue-800"> 👕 Clothes</div>
            <div className="text-xs text-gray-600 mt-1">
              Find Clothes
            </div>
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t py-4 mt-6">
        <div className="max-w-4xl mx-auto px-4 text-center text-gray-600 text-sm">
          <div className="flex items-center justify-center space-x-6 mb-2">
            <a href="#" className="hover:text-blue-600">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-blue-600">
              Terms of Service
            </a>
            <a href="#" className="hover:text-blue-600">
              Help Center
            </a>
          </div>
          <p>© 2023 Walmart Inc. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
