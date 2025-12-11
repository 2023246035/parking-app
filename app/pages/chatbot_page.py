import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
import asyncio


class ChatbotState(rx.State):
    """Enhanced chatbot state with better performance"""
    messages: list[dict[str, str]] = [
        {
            "role": "assistant", 
            "content": "👋 **Hey there! I'm your AI Parking Assistant**\n\nI can help you:\n• 🅿️ Find parking spots instantly\n• 📊 Check live availability\n• 💰 Compare prices\n• 📋 Manage your bookings\n\n**What can I help you with today?**"
        }
    ]
    current_message: str = ""
    is_loading: bool = False
    quick_actions: list[str] = [
        "🔍 Find parking near me",
        "📊 Check availability",
        "💰 Show cheapest spots",
        "⭐ Top rated lots"
    ]

    @rx.event
    async def on_load(self):
        """Check for query parameter and send message if present"""
        query_params = self.router.page.params
        if "query" in query_params:
            query = query_params["query"]
            if query and (not self.messages or self.messages[-1]["content"] != query):
                self.current_message = query
                return ChatbotState.send_message

    @rx.event
    async def send_quick_action(self, action: str):
        """Send a quick action message"""
        # Remove emoji and send
        clean_message = action.split(" ", 1)[1] if " " in action else action
        self.current_message = clean_message
        return ChatbotState.send_message

    @rx.event
    async def send_message(self):
        """Send a message to the AI - with streaming effect"""
        if not self.current_message.strip():
            return
        
        # Add user message
        user_msg = self.current_message
        self.messages.append({"role": "user", "content": user_msg})
        self.current_message = ""
        self.is_loading = True
        
        # Import here to avoid circular imports
        from app.services.ai.chatbot_ai import ParkingChatbot
        
        # Get AI response
        try:
            # Smaller delay for faster perceived performance
            await asyncio.sleep(0.3)
            response_data = await ParkingChatbot.generate_response(user_msg, user_id=None)
            response = response_data.get("response", "I'm sorry, I didn't get that.")
            
            # Add response
            self.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            self.messages.append({
                "role": "assistant", 
                "content": f"⚠️ **Oops! Something went wrong.**\n\nError: {str(e)}\n\nPlease try again or rephrase your question."
            })
        finally:
            self.is_loading = False


def message_bubble(message: dict) -> rx.Component:
    """Enhanced message bubble with markdown support"""
    is_user = message["role"] == "user"
    
    return rx.el.div(
        rx.el.div(
            # Assistant Avatar
            rx.cond(
                ~is_user,
                rx.el.div(
                    rx.el.div(
                        "AI",
                        class_name="text-xs font-bold text-white"
                    ),
                    class_name="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 via-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/40 mr-3 flex-shrink-0 animate-gradient"
                ),
                rx.fragment(),
            ),
            
            # Message Content with Markdown
            rx.el.div(
                rx.markdown(
                    message["content"],
                    class_name=rx.cond(
                        is_user,
                        "text-white prose prose-invert prose-sm max-w-none prose-headings:text-white prose-p:text-white prose-strong:text-white prose-a:text-blue-200",
                        "text-gray-800 prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-a:text-blue-600"
                    )
                ),
                class_name=rx.cond(
                    is_user,
                    "bg-gradient-to-br from-blue-600 via-blue-600 to-indigo-700 rounded-2xl rounded-tr-md px-5 py-4 shadow-lg shadow-blue-500/30 max-w-xl backdrop-blur-sm",
                    "bg-white/90 backdrop-blur-sm border border-gray-100 rounded-2xl rounded-tl-md px-5 py-4 shadow-md max-w-xl"
                ),
            ),
            
            # User Avatar
            rx.cond(
                is_user,
                rx.el.div(
                    rx.icon("user", class_name="w-4 h-4 text-blue-700"),
                    class_name="w-9 h-9 rounded-xl bg-blue-100 border border-blue-200 flex items-center justify-center ml-3 flex-shrink-0"
                ),
                rx.fragment(),
            ),
            
            class_name=rx.cond(
                is_user,
                "flex justify-end items-end mb-5 pl-16",
                "flex justify-start items-end mb-5 pr-16",
            ),
        ),
        class_name="w-full animate-in fade-in slide-in-from-bottom-3 duration-300"
    )


def quick_action_button(action: str) -> rx.Component:
    """Quick action chip button"""
    return rx.el.button(
        action,
        on_click=lambda: ChatbotState.send_quick_action(action),
        class_name="px-4 py-2.5 bg-gradient-to-r from-purple-50 to-indigo-50 hover:from-purple-100 hover:to-indigo-100 text-gray-700 rounded-xl text-sm font-medium border border-purple-200/50 hover:border-purple-300 transition-all duration-200 hover:shadow-md hover:scale-105 active:scale-95 whitespace-nowrap"
    )


def chatbot_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.div(
            # Animated Background
            rx.el.div(
                class_name="absolute inset-0 bg-gradient-to-br from-purple-50 via-white to-blue-50 -z-10"
            ),
            rx.el.div(
                class_name="absolute top-0 right-0 w-96 h-96 bg-purple-300/20 rounded-full blur-3xl animate-pulse -z-10"
            ),
            rx.el.div(
                class_name="absolute bottom-0 left-0 w-96 h-96 bg-blue-300/20 rounded-full blur-3xl animate-pulse delay-1000 -z-10"
            ),
            
            # Main Container
            rx.el.div(
                # Header
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            "✨",
                            class_name="text-5xl mb-3 animate-bounce"
                        ),
                        rx.el.h1(
                            "AI Parking Assistant",
                            class_name="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 mb-3 tracking-tight"
                        ),
                        rx.el.p(
                            "Your intelligent copilot for effortless parking",
                            class_name="text-xl text-gray-600 mb-8 font-medium"
                        ),
                        class_name="text-center"
                    ),
                    class_name="pt-8 pb-4"
                ),
                
                # Chat Container
                rx.el.div(
                    # Messages Area
                    rx.el.div(
                        # Quick Actions (shown at top)
                        rx.el.div(
                            rx.el.p(
                                "💡 Quick actions",
                                class_name="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3"
                            ),
                            rx.el.div(
                                rx.foreach(
                                    ChatbotState.quick_actions,
                                    quick_action_button
                                ),
                                class_name="flex gap-2 flex-wrap"
                            ),
                            class_name="mb-6 pb-6 border-b border-gray-100"
                        ),
                        
                        # Chat Messages
                        rx.foreach(
                            ChatbotState.messages,
                            message_bubble
                        ),
                        
                        # Typing Indicator
                        rx.cond(
                            ChatbotState.is_loading,
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        "AI",
                                        class_name="text-xs font-bold text-white"
                                    ),
                                    class_name="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 via-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/40 mr-3 animate-pulse"
                                ),
                                rx.el.div(
                                    rx.el.div(class_name="w-2.5 h-2.5 bg-purple-600 rounded-full animate-bounce"),
                                    rx.el.div(class_name="w-2.5 h-2.5 bg-purple-600 rounded-full animate-bounce [animation-delay:0.2s]"),
                                    rx.el.div(class_name="w-2.5 h-2.5 bg-purple-600 rounded-full animate-bounce [animation-delay:0.4s]"),
                                    class_name="bg-white/90 backdrop-blur-sm border border-gray-100 rounded-2xl rounded-tl-md px-5 py-4 shadow-md flex gap-2 items-center"
                                ),
                                class_name="flex justify-start items-end mb-5 animate-in fade-in duration-300"
                            ),
                        ),
                        
                        id="chat-messages",
                        class_name="flex-1 overflow-y-auto p-6 md:p-8 scroll-smooth scrollbar-thin scrollbar-thumb-purple-200 scrollbar-track-transparent"
                    ),
                    
                    # Input Area
                    rx.el.div(
                        rx.el.form(
                            rx.el.div(
                                # Input Field
                                rx.el.input(
                                    placeholder="Ask me anything about parking... (e.g., 'Find parking near KLCC')",
                                    value=ChatbotState.current_message,
                                    on_change=ChatbotState.set_current_message,
                                    disabled=ChatbotState.is_loading,
                                    class_name="flex-1 bg-transparent border-0 text-gray-900 placeholder-gray-400 focus:ring-0 px-5 py-4 text-base font-medium",
                                    auto_focus=True,
                                ),
                                
                                # Send Button
                                rx.el.button(
                                    rx.cond(
                                        ChatbotState.is_loading,
                                        rx.icon("loader-2", class_name="w-5 h-5 animate-spin"),
                                        rx.icon("send", class_name="w-5 h-5"),
                                    ),
                                    type="submit",
                                    disabled=ChatbotState.is_loading,
                                    class_name="mr-2 p-3 bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 text-white rounded-xl hover:shadow-lg hover:shadow-purple-500/50 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 animate-gradient"
                                ),
                                
                                class_name="flex items-center bg-gray-50/80 backdrop-blur-sm rounded-2xl border-2 border-gray-200 focus-within:border-purple-500 focus-within:ring-4 focus-within:ring-purple-500/10 transition-all duration-200"
                            ),
                            on_submit=ChatbotState.send_message,
                        ),
                        class_name="p-5 md:p-6 bg-white/95 backdrop-blur-xl border-t border-gray-100"
                    ),
                    
                    class_name="flex flex-col bg-white/70 backdrop-blur-2xl rounded-3xl shadow-2xl shadow-purple-200/50 border border-white/80 h-[700px] max-w-4xl mx-auto relative overflow-hidden ring-1 ring-gray-100"
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 pb-12 relative z-10"
            ),
        ),
        
        footer(),
        class_name="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 font-['Inter',sans-serif]",
        on_mount=ChatbotState.on_load
    )
