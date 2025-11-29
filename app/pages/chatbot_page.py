import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
import asyncio


class SimpleChatState(rx.State):
    """Simple chat state for the AI chatbot"""
    messages: list[dict[str, str]] = [
        {"role": "assistant", "content": "Hello! I'm your personal parking assistant. 🚗\n\nI can help you find spots, check prices, or predict availability. What can I do for you today?"}
    ]
    current_message: str = ""
    is_loading: bool = False

    @rx.event
    async def on_load(self):
        """Check for query parameter and send message if present"""
        query_params = self.router.page.params
        if "query" in query_params:
            query = query_params["query"]
            # Only send if it's a new query to avoid loops (simple check)
            if query and (not self.messages or self.messages[-1]["content"] != query):
                self.current_message = query
                return SimpleChatState.send_message

    @rx.event
    async def send_message(self):
        """Send a message to the AI"""
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
            # Simulate a small delay for "thinking" effect if response is too fast
            await asyncio.sleep(0.5) 
            response_data = await ParkingChatbot.generate_response(user_msg, user_id=None)
            response = response_data.get("response", "I'm sorry, I didn't get that.")
            self.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            self.messages.append({
                "role": "assistant", 
                "content": f"I'm having a bit of trouble connecting to my brain right now. 🤯\n\nError: {str(e)}"
            })
        finally:
            self.is_loading = False


def message_bubble(message: dict) -> rx.Component:
    """Render a chat message bubble with premium styling"""
    is_user = message["role"] == "user"
    
    return rx.el.div(
        rx.el.div(
            # Avatar
            rx.cond(
                ~is_user,
                rx.el.div(
                    rx.icon("bot", class_name="w-5 h-5 text-white"),
                    class_name="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 mr-3 flex-shrink-0"
                ),
                rx.fragment(),
            ),
            
            # Bubble
            rx.el.div(
                rx.el.p(
                    message["content"],
                    class_name=rx.cond(
                        is_user,
                        "text-white leading-relaxed",
                        "text-gray-800 leading-relaxed"
                    )
                ),
                class_name=rx.cond(
                    is_user,
                    "bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl rounded-tr-sm px-5 py-3.5 shadow-md shadow-blue-500/20 max-w-lg transform transition-all hover:scale-[1.01]",
                    "bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-5 py-3.5 shadow-sm max-w-lg"
                ),
            ),
            
            # User Avatar
            rx.cond(
                is_user,
                rx.el.div(
                    rx.icon("user", class_name="w-5 h-5 text-blue-600"),
                    class_name="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center ml-3 flex-shrink-0 border border-blue-100"
                ),
                rx.fragment(),
            ),
            
            class_name=rx.cond(
                is_user,
                "flex justify-end items-end mb-6 pl-12",
                "flex justify-start items-end mb-6 pr-12",
            ),
        ),
        class_name="w-full animate-in fade-in slide-in-from-bottom-2 duration-300"
    )


def chatbot_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.div(
            # Background Elements
            rx.el.div(
                class_name="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-indigo-50/50 to-transparent -z-10"
            ),
            rx.el.div(
                class_name="absolute top-20 right-0 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl -z-10 animate-pulse"
            ),
            
            # Main Container
            rx.el.div(
                # Header Section
                rx.el.div(
                    rx.el.h1(
                        "AI Parking Assistant",
                        class_name="text-4xl font-black text-gray-900 mb-3 tracking-tight"
                    ),
                    rx.el.p(
                        "Your intelligent copilot for finding the perfect spot.",
                        class_name="text-lg text-gray-500 mb-8"
                    ),
                    class_name="text-center pt-8"
                ),
                
                # Chat Interface
                rx.el.div(
                    # Messages Area
                    rx.el.div(
                        rx.foreach(
                            SimpleChatState.messages,
                            message_bubble
                        ),
                        
                        # Typing Indicator
                        rx.cond(
                            SimpleChatState.is_loading,
                            rx.el.div(
                                rx.el.div(
                                    rx.icon("bot", class_name="w-5 h-5 text-white"),
                                    class_name="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 mr-3"
                                ),
                                rx.el.div(
                                    rx.el.div(class_name="w-2 h-2 bg-gray-400 rounded-full animate-bounce"),
                                    rx.el.div(class_name="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"),
                                    rx.el.div(class_name="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"),
                                    class_name="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-4 shadow-sm flex gap-1.5 items-center h-12"
                                ),
                                class_name="flex justify-start items-end mb-6 animate-in fade-in duration-300"
                            ),
                        ),
                        
                        id="chat-messages",
                        class_name="flex-1 overflow-y-auto p-6 md:p-8 scroll-smooth"
                    ),
                    
                    # Input Area
                    rx.el.div(
                        rx.el.form(
                            rx.el.div(
                                rx.el.input(
                                    placeholder="Ask about parking availability, prices, or locations...",
                                    value=SimpleChatState.current_message,
                                    on_change=SimpleChatState.set_current_message,
                                    class_name="flex-1 bg-gray-50 border-0 text-gray-900 placeholder-gray-400 focus:ring-0 focus:bg-white transition-colors px-4 py-3 text-base",
                                    disabled=SimpleChatState.is_loading,
                                ),
                                rx.el.button(
                                    rx.cond(
                                        SimpleChatState.is_loading,
                                        rx.icon("loader-2", class_name="w-5 h-5 animate-spin"),
                                        rx.icon("send", class_name="w-5 h-5"),
                                    ),
                                    type="submit",
                                    disabled=SimpleChatState.is_loading,
                                    class_name="mx-2 p-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/30 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200",
                                ),
                                class_name="flex items-center bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10 transition-all duration-200 overflow-hidden p-1.5"
                            ),
                            on_submit=SimpleChatState.send_message,
                        ),
                        class_name="p-4 md:p-6 bg-white border-t border-gray-100 rounded-b-3xl"
                    ),
                    
                    class_name="flex flex-col bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-gray-200/50 border border-white/50 h-[650px] max-w-3xl mx-auto relative overflow-hidden"
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 pb-12 relative z-10"
            ),
        ),
        
        footer(),
        class_name="min-h-screen bg-gray-50 font-['Inter',sans-serif]",
        on_mount=SimpleChatState.on_load
    )
