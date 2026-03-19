import reflex as rx

def loading_overlay() -> rx.Component:
    """A premium full-page loading overlay that shows during hydration."""
    return rx.cond(
        ~rx.State.is_hydrated,
        rx.el.div(
            rx.el.div(
                # Centered content
                rx.el.div(
                    # Logo and Name
                    rx.el.div(
                        rx.icon("car-front", size=48, class_name="text-sky-500 mb-4 animate-bounce"),
                        rx.el.h2(
                            "ParkMyCar",
                            class_name="text-2xl font-bold text-gray-900 tracking-tight",
                        ),
                        class_name="flex flex-col items-center mb-8",
                    ),
                    
                    # Spinner
                    rx.el.div(
                        rx.spinner(size="3", class_name="text-sky-600"),
                        rx.el.p(
                            "Initializing secure connection...",
                            class_name="text-sm text-gray-500 mt-4 font-medium animate-pulse",
                        ),
                        class_name="flex flex-col items-center",
                    ),
                    class_name="bg-white/80 backdrop-blur-xl p-12 rounded-3xl shadow-2xl border border-white/20 flex flex-col items-center scale-100",
                ),
                class_name="relative z-10",
            ),
            
            # Background blur/gradient
            rx.el.div(
                class_name="absolute inset-0 bg-gradient-to-br from-sky-50 via-white to-indigo-50 opacity-90"
            ),
            rx.el.div(
                rx.el.div(
                    class_name="absolute top-1/4 left-1/4 w-64 h-64 bg-sky-200/40 rounded-full blur-3xl animate-pulse"
                ),
                rx.el.div(
                    class_name="absolute bottom-1/4 right-1/4 w-64 h-64 bg-indigo-200/40 rounded-full blur-3xl animate-pulse"
                ),
                class_name="absolute inset-0 overflow-hidden"
            ),
            
            class_name="fixed inset-0 z-[9999] flex items-center justify-center transition-all duration-500",
        ),
        rx.fragment()
    )
