import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer


def feature_card(icon: str, title: str, desc: str, color: str = "sky") -> rx.Component:
    """Enhanced feature card with hover effects and gradients"""
    color_classes = {
        "sky": {
            "bg": "from-sky-500 to-blue-600",
            "shadow": "shadow-sky-500/30",
            "hover_shadow": "group-hover:shadow-sky-500/50",
            "ring": "group-hover:ring-sky-400/50"
        },
        "purple": {
            "bg": "from-purple-500 to-indigo-600",
            "shadow": "shadow-purple-500/30",
            "hover_shadow": "group-hover:shadow-purple-500/50",
            "ring": "group-hover:ring-purple-400/50"
        },
        "emerald": {
            "bg": "from-emerald-500 to-teal-600",
            "shadow": "shadow-emerald-500/30",
            "hover_shadow": "group-hover:shadow-emerald-500/50",
            "ring": "group-hover:ring-emerald-400/50"
        }
    }
    
    colors = color_classes.get(color, color_classes["sky"])
    
    return rx.el.div(
        # Animated gradient background
        rx.el.div(
            class_name=f"absolute inset-0 bg-gradient-to-br {colors['bg']} opacity-0 group-hover:opacity-5 transition-opacity duration-500 rounded-3xl"
        ),
        # Icon container
        rx.el.div(
            rx.icon(icon, class_name="h-8 w-8 text-white"),
            class_name=f"relative h-16 w-16 rounded-2xl bg-gradient-to-br {colors['bg']} flex items-center justify-center mb-6 shadow-lg {colors['shadow']} {colors['hover_shadow']} group-hover:scale-110 group-hover:rotate-6 transition-all duration-500",
        ),
        # Title
        rx.el.h3(
            title,
            class_name="text-xl font-bold text-gray-900 mb-3 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:" + colors['bg'] + " transition-all duration-300"
        ),
        # Description
        rx.el.p(
            desc,
            class_name="text-gray-600 leading-relaxed"
        ),
        class_name=f"group relative p-8 rounded-3xl bg-white/80 backdrop-blur-sm border border-gray-100 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 hover:border-transparent hover:ring-2 {colors['ring']} hover:bg-white",
    )


def stat_card(number: str, label: str) -> rx.Component:
    """Animated stat cards"""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                number,
                class_name="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-sky-500 to-blue-600 mb-2"
            ),
            rx.el.div(
                label,
                class_name="text-gray-600 font-medium text-sm uppercase tracking-wide"
            ),
            class_name="text-center"
        ),
        class_name="p-8 rounded-2xl bg-white/60 backdrop-blur-sm border border-white/40 shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300"
    )


def home_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.main(
            # Hero Section
            rx.el.section(
                # Animated background gradients
                rx.el.div(
                    class_name="absolute top-0 left-0 w-96 h-96 bg-purple-300/20 rounded-full blur-3xl animate-pulse"
                ),
                rx.el.div(
                    class_name="absolute top-20 right-0 w-96 h-96 bg-sky-300/20 rounded-full blur-3xl animate-pulse delay-1000"
                ),
                rx.el.div(
                    class_name="absolute bottom-0 left-1/2 w-96 h-96 bg-indigo-300/20 rounded-full blur-3xl animate-pulse delay-500"
                ),
                
                rx.el.div(
                    rx.el.div(
                        # Left Content
                        rx.el.div(
                            # Badge
                            rx.el.span(
                                rx.icon("sparkles", class_name="inline h-4 w-4 mr-1.5"),
                                "New in Kuala Lumpur",
                                class_name="inline-flex items-center px-5 py-2 rounded-full bg-gradient-to-r from-sky-500/10 to-blue-500/10 text-sky-700 text-sm font-semibold mb-8 border border-sky-200/50 backdrop-blur-sm shadow-lg hover:scale-105 transition-transform duration-300"
                            ),
                            
                            # Main Heading
                            rx.el.h1(
                                "Smart Parking",
                                rx.el.br(),
                                "for the ",
                                rx.el.span(
                                    "Modern City",
                                    class_name="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 via-blue-600 to-indigo-600 animate-gradient"
                                ),
                                class_name="text-6xl md:text-7xl lg:text-8xl font-black text-gray-900 tracking-tight mb-6 leading-[1.05] drop-shadow-sm"
                            ),
                            
                            # Subheading
                            rx.el.p(
                                "Find and book parking spots instantly across Malaysia. ",
                                rx.el.span(
                                    "Real-time availability",
                                    class_name="font-semibold text-sky-600"
                                ),
                                ", secure payments, and hassle-free experience.",
                                class_name="text-xl md:text-2xl text-gray-600 mb-12 max-w-xl leading-relaxed"
                            ),
                            
                            # CTA Buttons
                            rx.el.div(
                                rx.el.a(
                                    rx.icon("search", class_name="h-5 w-5 mr-2"),
                                    "Find Parking",
                                    href="/listings",
                                    class_name="group inline-flex items-center px-8 py-4 rounded-2xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold text-lg shadow-2xl shadow-sky-500/50 hover:shadow-sky-500/70 hover:scale-105 hover:-translate-y-1 transition-all duration-300"
                                ),
                                rx.el.a(
                                    rx.icon("play-circle", class_name="h-5 w-5 mr-2"),
                                    "How it Works",
                                    href="/how-it-works",
                                    class_name="group inline-flex items-center px-8 py-4 rounded-2xl bg-white/80 backdrop-blur-sm text-gray-900 font-bold text-lg border-2 border-gray-200 hover:border-sky-500 hover:bg-white hover:scale-105 hover:-translate-y-1 transition-all duration-300 shadow-lg"
                                ),
                                class_name="flex flex-wrap gap-4"
                            ),
                            
                            # Trust badges
                            rx.el.div(
                                rx.el.div(
                                    rx.icon("shield-check", class_name="h-5 w-5 text-green-600 mr-2"),
                                    rx.el.span("Secure Payments", class_name="text-sm text-gray-600 font-medium"),
                                    class_name="flex items-center"
                                ),
                                rx.el.div(
                                    rx.icon("star", class_name="h-5 w-5 text-yellow-500 mr-2"),
                                    rx.el.span("4.9/5 Rating", class_name="text-sm text-gray-600 font-medium"),
                                    class_name="flex items-center"
                                ),
                                rx.el.div(
                                    rx.icon("users", class_name="h-5 w-5 text-sky-600 mr-2"),
                                    rx.el.span("10k+ Users", class_name="text-sm text-gray-600 font-medium"),
                                    class_name="flex items-center"
                                ),
                                class_name="flex flex-wrap gap-6 mt-12 pt-12 border-t border-gray-200"
                            ),
                            
                            class_name="flex-1 z-10"
                        ),
                        
                        # Right Image (Mobile Hidden)
                        rx.el.div(
                            # Decorative gradient orb
                            rx.el.div(
                                class_name="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-br from-sky-400/30 to-blue-600/30 rounded-full blur-3xl"
                            ),
                            # Placeholder for parking illustration
                            rx.el.div(
                                rx.icon("car-front", class_name="h-32 w-32 text-sky-500"),
                                class_name="relative bg-gradient-to-br from-white to-sky-50 rounded-3xl shadow-2xl shadow-sky-500/20 p-20 border border-white/50 backdrop-blur-sm transform hover:rotate-3 hover:scale-105 transition-all duration-700 flex items-center justify-center"
                            ),
                            class_name="flex-1 relative hidden lg:flex items-center justify-center"
                        ),
                        
                        class_name="relative flex items-center gap-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-24 md:py-32 min-h-[85vh]"
                    ),
                ),
                class_name="relative bg-gradient-to-br from-sky-50 via-white to-indigo-50/30 overflow-hidden"
            ),
            
            # Stats Section
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        stat_card("10k+", "Active Users"),
                        stat_card("500+", "Parking Spots"),
                        stat_card("50+", "Locations"),
                        stat_card("4.9", "Star Rating"),
                        class_name="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-6xl mx-auto px-6"
                    ),
                    class_name="py-16 -mt-16 relative z-10"
                )
            ),
            
            # Features Section
            rx.el.section(
                rx.el.div(
                    # Section Header
                    rx.el.div(
                        rx.el.span(
                            "FEATURES",
                            class_name="inline-block px-4 py-1.5 rounded-full bg-sky-100 text-sky-700 text-xs font-bold mb-4 uppercase tracking-wider"
                        ),
                        rx.el.h2(
                            "Why Choose ",
                            rx.el.span(
                                "ParkMyCar",
                                class_name="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-blue-600"
                            ),
                            "?",
                            class_name="text-5xl md:text-6xl font-black text-gray-900 text-center mb-4"
                        ),
                        rx.el.p(
                            "We make parking simple, secure, and stress-free with cutting-edge technology.",
                            class_name="text-xl text-gray-600 text-center mb-20 max-w-2xl mx-auto"
                        ),
                        class_name="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 text-center"
                    ),
                    
                    # Feature Cards Grid
                    rx.el.div(
                        feature_card(
                            "map-pin",
                            "Real-time Availability",
                            "See exactly how many spots are open before you arrive. Live updates every second. No more circling the block.",
                            "sky"
                        ),
                        feature_card(
                            "shield-check",
                            "Secure Payments",
                            "Pay safely with our integrated RinggitPay system. Bank-level encryption keeps your data protected.",
                            "purple"
                        ),
                        feature_card(
                            "zap",
                            "Instant Booking",
                            "Reserve your spot in seconds with our lightning-fast booking system. One tap and you're done.",
                            "emerald"
                        ),
                        feature_card(
                            "clock",
                            "Flexible Hours",
                            "Book for hours, days, or weeks. Extend your parking remotely if you need more time.",
                            "sky"
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12"
                    ),
                    
                    class_name="py-24 bg-gradient-to-b from-white to-gray-50 relative overflow-hidden"
                )
            ),
            
            # CTA Section
            rx.el.section(
                rx.el.div(
                    class_name="absolute inset-0 bg-gradient-to-br from-sky-600 via-blue-700 to-indigo-800"
                ),
                rx.el.div(
                    class_name="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjA1IiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-40"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("rocket", class_name="h-16 w-16 text-white mb-6 mx-auto"),
                        rx.el.h2(
                            "Ready to find your perfect parking spot?",
                            class_name="text-4xl md:text-5xl font-black text-white text-center mb-6 max-w-3xl mx-auto"
                        ),
                        rx.el.p(
                            "Join thousands of satisfied drivers parking smarter every day.",
                            class_name="text-xl text-sky-100 text-center mb-10 max-w-2xl mx-auto"
                        ),
                        rx.el.a(
                            "Get Started Now",
                            rx.icon("arrow-right", class_name="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform"),
                            href="/register",
                            class_name="group inline-flex items-center px-10 py-5 rounded-2xl bg-white text-blue-600 font-bold text-lg shadow-2xl hover:shadow-white/30 hover:scale-105 transition-all duration-300"
                        ),
                        class_name="relative z-10 max-w-7xl mx-auto px-6 text-center"
                    ),
                    class_name="relative py-24"
                ),
                class_name="relative overflow-hidden"
            ),
        ),
        
        footer(),
        
        class_name="font-['Roboto'] bg-white min-h-screen flex flex-col",
    )
