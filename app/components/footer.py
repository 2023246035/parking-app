import reflex as rx


def footer_column(title: str, links: list[tuple[str, str]]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            title,
            class_name="text-sm font-bold text-gray-900 uppercase tracking-wider mb-6",
        ),
        rx.el.ul(
            rx.foreach(
                links,
                lambda link: rx.el.li(
                    rx.el.a(
                        link[0],
                        href=link[1],
                        class_name="text-base text-gray-500 hover:text-sky-600 transition-colors duration-200",
                    ),
                    class_name="mb-3",
                ),
            ),
            class_name="space-y-2",
        ),
    )


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon("car-front", class_name="h-6 w-6 text-white"),
                            class_name="bg-gradient-to-br from-sky-500 to-blue-600 p-1.5 rounded-lg shadow-lg shadow-sky-500/20",
                        ),
                        rx.el.span(
                            "ParkMyCar",
                            class_name="text-2xl font-bold text-gray-900 tracking-tight",
                        ),
                        class_name="flex items-center gap-3 mb-6",
                    ),
                    rx.el.p(
                        "Making parking effortless across Malaysia. Find, book, and pay for parking spots in real-time.",
                        class_name="text-gray-500 text-sm max-w-xs leading-relaxed",
                    ),
                    class_name="col-span-1 md:col-span-2",
                ),
                footer_column(
                    "Product",
                    [("Features", "#"), ("Pricing", "#"), ("Enterprise", "#")],
                ),
                footer_column(
                    "Resources",
                    [("Blog", "#"), ("Documentation", "#"), ("Help Center", "#")],
                ),
                footer_column(
                    "Legal", [("Privacy", "#"), ("Terms", "#"), ("Cookie Policy", "#")]
                ),
                class_name="grid grid-cols-1 md:grid-cols-5 gap-8 py-16",
            ),
            rx.el.div(
                rx.el.p(
                    "© 2024 ParkMyCar Systems. All rights reserved.",
                    class_name="text-sm text-gray-400",
                ),
                rx.el.div(
                    rx.icon(
                        "facebook",
                        class_name="h-5 w-5 text-gray-400 hover:text-sky-600 hover:scale-110 transition-all cursor-pointer",
                    ),
                    rx.icon(
                        "twitter",
                        class_name="h-5 w-5 text-gray-400 hover:text-sky-600 hover:scale-110 transition-all cursor-pointer",
                    ),
                    rx.icon(
                        "instagram",
                        class_name="h-5 w-5 text-gray-400 hover:text-sky-600 hover:scale-110 transition-all cursor-pointer",
                    ),
                    class_name="flex gap-6",
                ),
                class_name="border-t border-gray-100 pt-8 flex flex-col md:flex-row justify-between items-center gap-4",
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
        ),
        class_name="bg-gradient-to-b from-white to-gray-50 border-t border-gray-100",
    )