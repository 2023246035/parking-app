import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer


def step_card(number: str, title: str, desc: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                number,
                class_name="text-6xl font-black text-sky-100 absolute -top-8 -left-4 select-none z-0",
            ),
            rx.el.div(
                rx.icon(icon, class_name="h-8 w-8 text-white"),
                class_name="h-16 w-16 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center mb-6 shadow-lg shadow-sky-500/20 relative z-10",
            ),
            class_name="relative",
        ),
        rx.el.h3(title, class_name="text-2xl font-bold text-gray-900 mb-4 relative z-10"),
        rx.el.p(desc, class_name="text-gray-600 leading-relaxed relative z-10"),
        class_name="relative p-8 rounded-3xl bg-white border border-gray-100 shadow-xl shadow-gray-200/40 hover:shadow-2xl hover:shadow-sky-100/50 transition-all duration-300 hover:-translate-y-1",
    )


def how_it_works_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "How ParkMyCar Works",
                            class_name="text-4xl md:text-5xl font-extrabold text-gray-900 text-center mb-6",
                        ),
                        rx.el.p(
                            "Your journey to hassle-free parking starts here. Follow these simple steps to secure your spot.",
                            class_name="text-xl text-gray-600 text-center max-w-2xl mx-auto mb-16",
                        ),
                        rx.el.div(
                            step_card(
                                "01",
                                "Find a Spot",
                                "Browse our extensive network of parking lots. Filter by location, price, or amenities to find the perfect match for your needs.",
                                "search",
                            ),
                            step_card(
                                "02",
                                "Book Instantly",
                                "Select your date, time, and duration. Our real-time system ensures the spot is reserved just for you.",
                                "calendar-check",
                            ),
                            step_card(
                                "03",
                                "Secure Payment",
                                "Pay securely using RinggitPay. We support all major credit cards and online banking options.",
                                "credit-card",
                            ),
                            step_card(
                                "04",
                                "Park & Relax",
                                "Drive to the location and park. You can manage or cancel your booking easily if plans change.",
                                "car",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8",
                        ),
                        class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
                    ),
                    class_name="py-24 bg-gradient-to-b from-sky-50 to-white",
                )
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Frequently Asked Questions",
                            class_name="text-3xl font-bold text-gray-900 text-center mb-12",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.h3("Can I cancel my booking?", class_name="text-lg font-bold text-gray-900 mb-2"),
                                rx.el.p("Yes! We offer flexible cancellation policies. You can get a full refund if you cancel 24 hours before your booking starts.", class_name="text-gray-600"),
                                class_name="bg-gray-50 p-6 rounded-2xl",
                            ),
                            rx.el.div(
                                rx.el.h3("Is payment secure?", class_name="text-lg font-bold text-gray-900 mb-2"),
                                rx.el.p("Absolutely. We use industry-standard encryption and partner with trusted payment gateways to ensure your data is safe.", class_name="text-gray-600"),
                                class_name="bg-gray-50 p-6 rounded-2xl",
                            ),
                            rx.el.div(
                                rx.el.h3("What if I arrive late?", class_name="text-lg font-bold text-gray-900 mb-2"),
                                rx.el.p("Your spot is reserved for the entire duration of your booking. However, we recommend arriving on time to maximize your parking window.", class_name="text-gray-600"),
                                class_name="bg-gray-50 p-6 rounded-2xl",
                            ),
                            rx.el.div(
                                rx.el.h3("Do I need to print anything?", class_name="text-lg font-bold text-gray-900 mb-2"),
                                rx.el.p("No printing needed! Just show your booking confirmation on your phone to the parking attendant or scan the QR code at the entry.", class_name="text-gray-600"),
                                class_name="bg-gray-50 p-6 rounded-2xl",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto",
                        ),
                        class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
                    ),
                    class_name="py-24 bg-white",
                )
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2("Ready to get started?", class_name="text-3xl font-bold text-white mb-6"),
                        rx.el.p("Join thousands of happy drivers who save time and money with ParkMyCar.", class_name="text-sky-100 text-lg mb-8 max-w-2xl mx-auto"),
                        rx.el.a(
                            rx.el.button(
                                "Find Parking Now",
                                class_name="bg-white text-sky-600 px-8 py-4 rounded-2xl font-bold hover:shadow-lg hover:scale-105 transition-all",
                            ),
                            href="/listings",
                        ),
                        class_name="text-center",
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 bg-gradient-to-r from-sky-500 to-blue-600 rounded-3xl mx-4 sm:mx-6 lg:mx-8 mb-24 shadow-2xl shadow-sky-500/30",
                )
            ),
        ),
        footer(),
        class_name="font-['Roboto'] min-h-screen flex flex-col",
    )
