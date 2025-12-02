import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer


def feature_card(icon: str, title: str, desc: str, color: str = "indigo") -> rx.Component:
    """Enhanced feature card with glassmorphism and hover effects"""
    color_map = {
        "indigo": "from-indigo-500 to-purple-600",
        "pink": "from-pink-500 to-rose-600",
        "cyan": "from-cyan-500 to-blue-600",
        "emerald": "from-emerald-500 to-teal-600",
    }
    gradient = color_map.get(color, color_map["indigo"])
    
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="w-8 h-8 text-white"),
            class_name=f"w-14 h-14 rounded-2xl bg-gradient-to-br {gradient} flex items-center justify-center mb-6 shadow-lg transform group-hover:scale-110 group-hover:-rotate-3 transition-all duration-300"
        ),
        rx.el.h3(
            title,
            class_name="text-xl font-bold text-gray-900 mb-3 group-hover:text-indigo-600 transition-colors"
        ),
        rx.el.p(
            desc,
            class_name="text-gray-600 leading-relaxed text-sm"
        ),
        class_name="group p-8 bg-white rounded-3xl border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
    )


def stat_card(number: str, label: str) -> rx.Component:
    """Minimalist animated stat card"""
    return rx.el.div(
        rx.el.p(
            number,
            class_name="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-1"
        ),
        rx.el.p(
            label,
            class_name="text-sm font-medium text-gray-500 uppercase tracking-wider"
        ),
        class_name="text-center p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-white/60 shadow-sm hover:shadow-md transition-all"
    )


def home_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.main(
            # Hero Section
            rx.el.section(
                # Background Elements
                rx.el.div(
                    class_name="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-100 via-white to-white -z-10"
                ),
                rx.el.div(
                    class_name="absolute top-20 right-0 w-[500px] h-[500px] bg-purple-200/40 rounded-full blur-[100px] -z-10 animate-pulse"
                ),
                rx.el.div(
                    class_name="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-200/40 rounded-full blur-[100px] -z-10 animate-pulse delay-700"
                ),
                
                rx.el.div(
                    rx.el.div(
                        # Left Content
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    "✨ The Future of Parking",
                                    class_name="px-4 py-1.5 rounded-full bg-indigo-50 text-indigo-700 text-sm font-semibold border border-indigo-100 inline-block mb-6"
                                ),
                                rx.el.h1(
                                    "Parking Made ",
                                    rx.el.span(
                                        "Effortless",
                                        class_name="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600"
                                    ),
                                    rx.el.br(),
                                    "& Intelligent",
                                    class_name="text-6xl md:text-7xl lg:text-8xl font-black text-gray-900 tracking-tight mb-6 leading-[1.1]"
                                ),
                                rx.el.p(
                                    "Experience seamless parking with AI-driven recommendations, real-time availability, and instant bookings. Your perfect spot is waiting.",
                                    class_name="text-xl text-gray-600 mb-10 max-w-xl leading-relaxed"
                                ),
                                
                                # CTA Buttons
                                rx.el.div(
                                    rx.el.a(
                                        "Find Parking Now",
                                        rx.icon("arrow-right", class_name="w-5 h-5 ml-2"),
                                        href="/listings",
                                        class_name="group inline-flex items-center px-8 py-4 rounded-full bg-gray-900 text-white font-bold text-lg shadow-lg hover:bg-gray-800 hover:scale-105 hover:shadow-xl transition-all duration-300"
                                    ),
                                    rx.el.a(
                                        rx.icon("play", class_name="w-5 h-5 mr-2"),
                                        "How it Works",
                                        href="/how-it-works",
                                        class_name="inline-flex items-center px-8 py-4 rounded-full bg-white text-gray-900 font-bold text-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-300"
                                    ),
                                    class_name="flex flex-wrap gap-4"
                                ),
                                
                                # Stats Row
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.div(
                                            rx.el.p("4.9/5", class_name="font-bold text-gray-900"),
                                            rx.el.div(
                                                rx.icon("star", class_name="w-4 h-4 text-yellow-400 fill-yellow-400"),
                                                rx.icon("star", class_name="w-4 h-4 text-yellow-400 fill-yellow-400"),
                                                rx.icon("star", class_name="w-4 h-4 text-yellow-400 fill-yellow-400"),
                                                rx.icon("star", class_name="w-4 h-4 text-yellow-400 fill-yellow-400"),
                                                rx.icon("star", class_name="w-4 h-4 text-yellow-400 fill-yellow-400"),
                                                class_name="flex gap-0.5"
                                            ),
                                            class_name="flex flex-col"
                                        ),
                                        rx.el.div(class_name="w-px h-10 bg-gray-200"),
                                        rx.el.div(
                                            rx.el.p("10k+", class_name="font-bold text-gray-900"),
                                            rx.el.p("Happy Users", class_name="text-sm text-gray-500"),
                                            class_name="flex flex-col"
                                        ),
                                        rx.el.div(class_name="w-px h-10 bg-gray-200"),
                                        rx.el.div(
                                            rx.el.p("24/7", class_name="font-bold text-gray-900"),
                                            rx.el.p("Support", class_name="text-sm text-gray-500"),
                                            class_name="flex flex-col"
                                        ),
                                        class_name="flex items-center gap-8 mt-12 pt-8 border-t border-gray-100"
                                    ),
                                ),
                                class_name="flex-1 z-10"
                            ),
                            
                            # Right Visual
                            rx.el.div(
                                rx.el.div(
                                    # Abstract decorative shapes
                                    rx.el.div(class_name="absolute top-10 right-10 w-20 h-20 bg-yellow-400 rounded-full blur-2xl opacity-20 animate-bounce"),
                                    rx.el.div(class_name="absolute bottom-10 left-10 w-32 h-32 bg-purple-500 rounded-full blur-3xl opacity-20 animate-pulse"),
                                    
                                    # Main Image Card
                                    rx.el.div(
                                        rx.el.img(
                                            src="https://images.unsplash.com/photo-1573348722427-f1d6819fdf98?auto=format&fit=crop&w=800&q=80",
                                            alt="Smart Parking",
                                            class_name="rounded-3xl shadow-2xl w-full object-cover h-[500px]"
                                        ),
                                        # Floating Badge 1
                                        rx.el.div(
                                            rx.icon("check", class_name="w-6 h-6 text-green-500 mr-3"),
                                            rx.el.div(
                                                rx.el.p("Spot Reserved", class_name="font-bold text-gray-900 text-sm"),
                                                rx.el.p("Zone A - Slot 42", class_name="text-xs text-gray-500"),
                                            ),
                                            class_name="absolute -left-8 top-20 bg-white p-4 rounded-2xl shadow-xl flex items-center animate-[bounce_3s_infinite]"
                                        ),
                                        # Floating Badge 2
                                        rx.el.div(
                                            rx.icon("clock", class_name="w-6 h-6 text-indigo-500 mr-3"),
                                            rx.el.div(
                                                rx.el.p("Time Remaining", class_name="font-bold text-gray-900 text-sm"),
                                                rx.el.p("01:45:00", class_name="text-xs text-indigo-600 font-mono"),
                                            ),
                                            class_name="absolute -right-8 bottom-20 bg-white p-4 rounded-2xl shadow-xl flex items-center animate-[bounce_4s_infinite]"
                                        ),
                                        class_name="relative transform rotate-2 hover:rotate-0 transition-all duration-500"
                                    ),
                                    class_name="relative w-full max-w-lg mx-auto"
                                ),
                                class_name="flex-1 hidden lg:flex items-center justify-center"
                            ),
                            class_name="flex flex-col lg:flex-row items-center gap-16"
                        ),
                        class_name="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-20 lg:py-32"
                    ),
                ),
                class_name="relative overflow-hidden"
            ),
            
            # AI Features Section
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Powered by Intelligence",
                            class_name="text-3xl md:text-4xl font-black text-gray-900 mb-4 text-center"
                        ),
                        rx.el.p(
                            "Advanced AI features designed to make your parking experience smarter.",
                            class_name="text-xl text-gray-600 max-w-2xl mx-auto text-center mb-16"
                        ),
                        
                        rx.el.div(
                            # AI Chatbot Card
                            rx.el.a(
                                rx.el.div(
                                    rx.el.div(
                                        rx.icon("message-square", class_name="w-8 h-8 text-white"),
                                        class_name="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mb-6 shadow-lg shadow-purple-500/20"
                                    ),
                                    rx.el.h3("AI Assistant", class_name="text-2xl font-bold text-gray-900 mb-3"),
                                    rx.el.p(
                                        "Chat with our smart assistant to find spots, check rates, and get instant answers.",
                                        class_name="text-gray-600 mb-6"
                                    ),
                                    rx.el.div(
                                        "Try Chatbot",
                                        rx.icon("arrow-right", class_name="w-4 h-4 ml-2"),
                                        class_name="text-purple-600 font-bold flex items-center group-hover:translate-x-2 transition-transform"
                                    ),
                                    class_name="h-full p-8 bg-white rounded-[2rem] border border-gray-100 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 group"
                                ),
                                href="/chatbot",
                                class_name="col-span-1 md:col-span-2 lg:col-span-1"
                            ),
                            
                            # Auto Booking Card
                            rx.el.a(
                                rx.el.div(
                                    rx.el.div(
                                        rx.icon("zap", class_name="w-8 h-8 text-white"),
                                        class_name="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center mb-6 shadow-lg shadow-blue-500/20"
                                    ),
                                    rx.el.h3("Smart Auto-Booking", class_name="text-2xl font-bold text-gray-900 mb-3"),
                                    rx.el.p(
                                        "Set your preferences and let AI automatically book your favorite spots.",
                                        class_name="text-gray-600 mb-6"
                                    ),
                                    rx.el.div(
                                        "Configure Now",
                                        rx.icon("arrow-right", class_name="w-4 h-4 ml-2"),
                                        class_name="text-blue-600 font-bold flex items-center group-hover:translate-x-2 transition-transform"
                                    ),
                                    class_name="h-full p-8 bg-white rounded-[2rem] border border-gray-100 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 group"
                                ),
                                href="/smart-dashboard",
                                class_name="col-span-1 md:col-span-2 lg:col-span-1"
                            ),
                            
                            # Dynamic Pricing Card
                            rx.el.div(
                                rx.el.div(
                                    rx.icon("trending-up", class_name="w-8 h-8 text-white"),
                                    class_name="w-16 h-16 rounded-2xl bg-gradient-to-br from-rose-500 to-orange-600 flex items-center justify-center mb-6 shadow-lg shadow-rose-500/20"
                                ),
                                rx.el.h3("Dynamic Pricing", class_name="text-2xl font-bold text-gray-900 mb-3"),
                                rx.el.p(
                                    "Fair, real-time pricing based on demand to ensure optimal availability.",
                                    class_name="text-gray-600 mb-6"
                                ),
                                rx.el.div(
                                    "Learn More",
                                    rx.icon("arrow-right", class_name="w-4 h-4 ml-2"),
                                    class_name="text-rose-600 font-bold flex items-center group-hover:translate-x-2 transition-transform"
                                ),
                                class_name="h-full p-8 bg-white rounded-[2rem] border border-gray-100 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 group col-span-1 md:col-span-2 lg:col-span-1"
                            ),
                            
                            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                        ),
                        class_name="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12"
                    ),
                    class_name="py-24 bg-gray-50"
                )
            ),
            
            # Why Choose Us Grid
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Why Choose ParkMyCar?",
                            class_name="text-3xl md:text-4xl font-black text-gray-900 mb-16 text-center"
                        ),
                        rx.el.div(
                            feature_card(
                                "map-pin",
                                "Real-time Availability",
                                "Live updates on parking spots so you never have to circle the block again.",
                                "cyan"
                            ),
                            feature_card(
                                "shield-check",
                                "Secure Payments",
                                "Bank-grade encryption ensures your payment data is always protected.",
                                "emerald"
                            ),
                            feature_card(
                                "clock",
                                "Flexible Booking",
                                "Book for an hour or a month. Extend your session remotely with one tap.",
                                "indigo"
                            ),
                            feature_card(
                                "bell",
                                "Smart Alerts",
                                "Get notified before your parking expires and when spots open up.",
                                "pink"
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
                        ),
                        class_name="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12"
                    ),
                    class_name="py-24 bg-white"
                )
            ),
            
            # CTA Section
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Ready to Park Smarter?",
                            class_name="text-4xl md:text-5xl font-black text-white mb-6"
                        ),
                        rx.el.p(
                            "Join thousands of happy drivers and stop worrying about parking today.",
                            class_name="text-xl text-indigo-100 mb-10 max-w-2xl mx-auto"
                        ),
                        rx.el.a(
                            "Get Started for Free",
                            href="/register",
                            class_name="inline-block px-10 py-4 rounded-full bg-white text-indigo-600 font-bold text-lg shadow-lg hover:bg-indigo-50 hover:scale-105 transition-all duration-300"
                        ),
                        class_name="relative z-10 max-w-4xl mx-auto text-center px-6"
                    ),
                    class_name="relative py-32 bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900 overflow-hidden"
                ),
            ),
        ),
        
        footer(),
        
        class_name="font-['Roboto'] min-h-screen flex flex-col bg-white",
    )
