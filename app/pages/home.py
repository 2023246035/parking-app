import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer


def feature_card(icon: str, title: str, desc: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-7 w-7 text-white"),
            class_name="h-14 w-14 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center mb-6 shadow-lg shadow-sky-500/20 group-hover:scale-110 transition-transform duration-300",
        ),
        rx.el.h3(title, class_name="text-xl font-bold text-gray-900 mb-3"),
        rx.el.p(desc, class_name="text-gray-600 leading-relaxed"),
        class_name="group p-8 rounded-3xl bg-white/60 backdrop-blur-sm border border-white/20 shadow-xl shadow-gray-200/40 hover:shadow-2xl hover:shadow-sky-100/50 transition-all duration-300 hover:-translate-y-1",
    )


def home_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "New in Kuala Lumpur",
                                class_name="inline-block px-4 py-1.5 rounded-full bg-sky-100/50 text-sky-700 text-sm font-semibold mb-6 border border-sky-200 backdrop-blur-sm",
                            ),
                            rx.el.h1(
                                "Smart Parking for the",
                                rx.el.br(),
                                rx.el.span(
                                    "Modern City",
                                    class_name="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 via-blue-600 to-indigo-600",
                                ),
                                class_name="text-5xl md:text-7xl font-extrabold text-gray-900 tracking-tight mb-6 leading-[1.1] drop-shadow-sm",
                            ),
                            rx.el.p(
                                "Find and book parking spots instantly across Malaysia. Real-time availability, secure payments, and hassle-free experience.",
                                class_name="text-xl text-gray-600 mb-10 max-w-lg leading-relaxed",
                            ),
                            rx.el.div(
                                rx.el.a(
                                    rx.el.button(
                                        "Find Parking Now",
                                        class_name="bg-gradient-to-r from-sky-500 to-blue-600 text-white px-8 py-4 rounded-2xl hover:shadow-lg hover:shadow-sky-500/40 hover:scale-105 active:scale-95 transition-all font-semibold text-lg",
                                    ),
                                    href="/listings",
                                ),
                                rx.el.button(
                                    "How it Works",
                                    class_name="bg-white/80 backdrop-blur-sm text-gray-700 px-8 py-4 rounded-2xl hover:bg-white transition-all border border-white/20 shadow-sm hover:shadow-md font-semibold text-lg",
                                ),
                                class_name="flex flex-col sm:flex-row gap-4",
                            ),
                            class_name="flex-1 z-10",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="absolute top-0 right-0 w-[600px] h-[600px] bg-sky-200/30 rounded-full blur-3xl -z-10 animate-pulse"
                            ),
                            rx.image(
                                src="/placeholder.svg",
                                class_name="w-full h-auto rounded-3xl shadow-[0_20px_50px_rgb(0,0,0,0.1)] border border-white/50 backdrop-blur-sm transform rotate-2 hover:rotate-0 transition-transform duration-700 hover:scale-[1.02]",
                            ),
                            class_name="flex-1 relative hidden md:block",
                        ),
                        class_name="flex items-center gap-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32",
                    ),
                    class_name="bg-gradient-to-br from-sky-50 via-white to-indigo-50/30 min-h-[90vh]",
                )
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Why Choose ParkMyCar?",
                            class_name="text-4xl font-bold text-gray-900 text-center mb-4",
                        ),
                        rx.el.p(
                            "We make parking simple, secure, and stress-free.",
                            class_name="text-xl text-gray-600 text-center mb-16 max-w-2xl mx-auto",
                        ),
                        class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
                    ),
                    rx.el.div(
                        feature_card(
                            "map",
                            "Real-time Availability",
                            "See exactly how many spots are open before you arrive. No more circling the block.",
                        ),
                        feature_card(
                            "shield-check",
                            "Secure Payments",
                            "Pay safely with our integrated RinggitPay system. Your data is always protected.",
                        ),
                        feature_card(
                            "clock",
                            "Easy Booking",
                            "Reserve your spot in seconds. Flexible cancellation policies if your plans change.",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
                    ),
                    class_name="py-32 bg-white relative overflow-hidden",
                )
            ),
        ),
        footer(),
        class_name="font-['Roboto'] bg-white min-h-screen flex flex-col",
    )