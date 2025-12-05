import reflex as rx
from app.states.analytics_state import AnalyticsState
from app.pages.admin_users import admin_navbar

def admin_analytics_page() -> rx.Component:
    return rx.el.div(
        admin_navbar(),
        rx.el.main(
            rx.el.div(
                rx.el.h1("Analytics Dashboard", class_name="text-3xl font-bold mb-6"),
                
                # Charts Section
                rx.el.div(
                    # Bookings Chart
                    rx.el.div(
                        rx.el.h3("Bookings (Last 7 Days)", class_name="text-lg font-semibold mb-4"),
                        rx.recharts.line_chart(
                            rx.recharts.line(
                                data_key="bookings",
                                stroke="#8884d8",
                            ),
                            rx.recharts.x_axis(data_key="date"),
                            rx.recharts.y_axis(),
                            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                            rx.recharts.tooltip(),
                            data=AnalyticsState.bookings_data,
                            height=300,
                        ),
                        class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                    ),
                    # Revenue Chart
                    rx.el.div(
                        rx.el.h3("Revenue (Last 7 Days)", class_name="text-lg font-semibold mb-4"),
                        rx.recharts.bar_chart(
                            rx.recharts.bar(
                                data_key="revenue",
                                fill="#82ca9d",
                            ),
                            rx.recharts.x_axis(data_key="date"),
                            rx.recharts.y_axis(),
                            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                            rx.recharts.tooltip(),
                            data=AnalyticsState.revenue_data,
                            height=300,
                        ),
                        class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
                ),
                
                # Lot Stats Table
                rx.el.div(
                    rx.el.h3("Parking Lot Performance", class_name="text-lg font-semibold mb-4"),
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Parking Lot", class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                rx.el.th("Occupancy", class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                rx.el.th("Total Bookings", class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                rx.el.th("Revenue", class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
                            ),
                            class_name="bg-gray-50"
                        ),
                        rx.el.tbody(
                            rx.foreach(
                                AnalyticsState.lot_stats,
                                lambda lot: rx.el.tr(
                                    rx.el.td(lot["name"], class_name="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"),
                                    rx.el.td(f"{lot['occupancy']}%", class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500"),
                                    rx.el.td(lot["total_bookings"], class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500"),
                                    rx.el.td(f"RM {lot['revenue']}", class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500"),
                                    class_name="bg-white border-b border-gray-100"
                                )
                            )
                        ),
                        class_name="min-w-full divide-y divide-gray-200"
                    ),
                    class_name="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-8"
                ),
                
                # Refund Metrics
                rx.el.div(
                    rx.el.h3("Refund Metrics", class_name="text-lg font-semibold mb-4"),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p("Total Refunds", class_name="text-sm text-gray-500"),
                            rx.el.p(AnalyticsState.refund_stats["total_refunds"], class_name="text-2xl font-bold text-gray-900"),
                            class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                        ),
                        rx.el.div(
                            rx.el.p("Refund Amount", class_name="text-sm text-gray-500"),
                            rx.el.p(f"RM {AnalyticsState.refund_stats['refund_amount']}", class_name="text-2xl font-bold text-gray-900"),
                            class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                        ),
                        rx.el.div(
                            rx.el.p("Refund Rate", class_name="text-sm text-gray-500"),
                            rx.el.p(f"{AnalyticsState.refund_stats['refund_rate']}%", class_name="text-2xl font-bold text-gray-900"),
                            class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-3 gap-6"
                    )
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
            ),
            class_name="bg-gray-50 min-h-screen"
        ),
        on_mount=AnalyticsState.load_analytics
    )
