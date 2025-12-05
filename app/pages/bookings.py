import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
from app.components.cancellation_modal import cancellation_modal
from app.states.booking_state import BookingState, Booking
from app.states.auth_state import AuthState


def booking_status_badge(status: str) -> rx.Component:
    """Minimalist status badges"""
    return rx.match(
        status,
       (" Confirmed",
            rx.el.span(
                "● Confirmed",
                class_name="text-xs font-semibold text-green-600"
            ),
        ),
        (
            "Pending",
            rx.el.span(
                "● Pending",
                class_name="text-xs font-semibold text-yellow-600"
            ),
        ),
        (
            "Cancelled",
            rx.el.span(
                "● Cancelled",
                class_name="text-xs font-semibold text-red-600"
            ),
        ),
        (
            "Completed",
            rx.el.span(
                "● Completed",
                class_name="text-xs font-semibold text-gray-600"
            ),
        ),
        rx.el.span(
            f"● {status}",
            class_name="text-xs font-semibold text-gray-600"
        ),
    )


from datetime import datetime

# Client-side JavaScript for robust ticket generation
TICKET_JS = """
const generateTicketHtml = (data, isWord) => {
    const headerBg = isWord ? '#4f46e5' : 'linear-gradient(135deg, #4f46e5, #7c3aed)';
    
    // Ensure data values are strings and handle potential undefined/nulls
    const safe = (val) => val || 'N/A';
    
    let html = `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Parking Ticket</title>
        <style>
            body { font-family: sans-serif; background-color: #f3f4f6; padding: 20px; }
            .ticket { background: white; max-width: 600px; margin: 0 auto; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .header { background: ${headerBg}; color: white; padding: 30px; text-align: center; }
            .content { padding: 30px; }
            table { width: 100%; border-collapse: collapse; }
            td { padding: 12px 0; border-bottom: 1px dashed #e5e7eb; }
            .label { color: #6b7280; font-size: 14px; }
            .value { text-align: right; font-weight: bold; color: #111827; }
            .total { color: #166534; font-size: 18px; }
            .footer { background: #f9fafb; padding: 20px; text-align: center; color: #9ca3af; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="ticket">
            <div class="header">
                <h1 style="margin:0;font-size:24px">PARKING RECEIPT</h1>
                <p style="margin:5px 0 0 0;opacity:0.9">#${safe(data.id)}</p>
            </div>
            <div class="content">
                <table>
                    <tr><td class="label">Location</td><td class="value">${safe(data.lot_name)}</td></tr>
                    <tr><td class="label">Date</td><td class="value">${safe(data.start_date)}</td></tr>
                    <tr><td class="label">Time</td><td class="value">${safe(data.start_time)}</td></tr>
                    <tr><td class="label">Duration</td><td class="value">${safe(data.duration_hours)} Hours</td></tr>
                    <tr><td class="label">Slot</td><td class="value">${safe(data.slot_id)}</td></tr>
                    <tr><td class="label">Vehicle</td><td class="value">${safe(data.vehicle_number)}</td></tr>
                    <tr><td class="label">Phone</td><td class="value">${safe(data.phone_number)}</td></tr>
                    <tr><td class="label">Status</td><td class="value">${safe(data.status)}</td></tr>
                    <tr><td class="label">Total Paid</td><td class="value total">RM ${safe(data.total_price)}</td></tr>
                </table>
            </div>
            <div class="footer">
                Thank you for using Smart Parking App<br>
                Generated on ${new Date().toLocaleDateString()}
            </div>
        </div>
        ${!isWord ? '<script>window.onload=function(){window.print()}</script>' : ''}
    </body>
    </html>
    `;
    return html;
};

window.downloadWordTicket = (data) => {
    try {
        const html = generateTicketHtml(data, true);
        const blob = new Blob(['\\ufeff', html], { type: 'application/msword' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `ticket_${data.id}.doc`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error("Error downloading ticket:", e);
        alert("Failed to download ticket. Please try again.");
    }
};

window.printTicket = (data) => {
    console.log("=== printTicket called ===");
    console.log("Data received:", data);
    
    try {
        const html = generateTicketHtml(data, false);
        console.log("HTML generated successfully");
        
        const printWindow = window.open('', '_blank', 'width=800,height=600');
        console.log("Popup window opened:", !!printWindow);
        
        if (printWindow) {
            printWindow.document.write(html);
            printWindow.document.close();
            // Give time for content to load before printing
            printWindow.focus();
            console.log("✅ Print window created successfully");
        } else {
            // Fallback: Use iframe if popup is blocked
            console.log("⚠️ Popup blocked, using iframe method");
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            document.body.appendChild(iframe);
            
            const iframeDoc = iframe.contentWindow.document;
            iframeDoc.write(html);
            iframeDoc.close();
            
            // Wait for content to load
            iframe.onload = function() {
                console.log("iframe loaded, triggering print");
                iframe.contentWindow.focus();
                iframe.contentWindow.print();
                
                // Remove iframe after printing
                setTimeout(() => {
                    document.body.removeChild(iframe);
                    console.log("iframe removed");
                }, 1000);
            };
            
            // Trigger onload manually if it doesn't fire
            setTimeout(() => {
                if (iframe.contentWindow) {
                    console.log("Manual iframe print trigger");
                    iframe.contentWindow.focus();
                    iframe.contentWindow.print();
                    setTimeout(() => {
                        try { document.body.removeChild(iframe); } catch(e) {}
                    }, 1000);
                }
            }, 500);
        }
    } catch (e) {
        console.error("❌ Error printing ticket:", e);
        alert("Failed to print ticket. Error: " + e.message + "\\nCheck console for details.");
    }
};

// Verify function is defined
console.log("✅ window.printTicket defined:", typeof window.printTicket);
"""

def payment_status_badge(status: str) -> rx.Component:
    """Minimal payment badges"""
    return rx.match(
        status,
        (
            "Paid",
            rx.el.span(
                "✓ Paid",
                class_name="text-xs font-medium text-green-700 bg-green-50 px-2.5 py-1 rounded-md"
            ),
        ),
        (
            "Refunded",
            rx.el.span(
                "↺ Refunded",
                class_name="text-xs font-medium text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md"
            ),
        ),
        (
            "Pending",
            rx.el.span(
                "○ Pending",
                class_name="text-xs font-medium text-yellow-700 bg-yellow-50 px-2.5 py-1 rounded-md"
            ),
        ),
        rx.el.span(status, class_name="text-xs text-gray-600"),
    )


def generate_ticket_doc(booking: Booking) -> rx.Var:
    """Generates a Word-compatible HTML ticket as a data URI"""
    
    # We use a table-based layout which is most compatible with Word
    return (
        "data:application/msword;charset=utf-8," +
        "%3Chtml xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'%3E" +
        "%3Chead%3E%3Cmeta charset='utf-8'%3E%3Ctitle%3EParking Ticket%3C/title%3E%3C/head%3E" +
        "%3Cbody style='font-family:Arial,sans-serif'%3E" +
        
        # Container
        "%3Cdiv style='width:100%;max-width:600px;margin:0 auto;border:1px solid #ddd;padding:0'%3E" +
        
        # Header
        "%3Cdiv style='background-color:#4f46e5;color:white;padding:20px;text-align:center'%3E" +
        "%3Ch2 style='margin:0'%3EPARKING TICKET%3C/h2%3E" +
        "%3Cp style='margin:5px 0 0 0'%3EOfficial Receipt%3C/p%3E" +
        "%3C/div%3E" +
        
        # Content Table
        "%3Ctable style='width:100%;border-collapse:collapse;margin:20px 0'%3E" +
        
        # Rows
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3EBooking ID%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + booking.id + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3ELocation%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + booking.lot_name + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3ESlot%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + rx.cond(booking.slot_id != "", booking.slot_id, "N/A") + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3EDate%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + booking.start_date + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3ETime%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + booking.start_time + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3EVehicle%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + rx.cond(booking.vehicle_number != "", booking.vehicle_number, "N/A") + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3EContact%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + rx.cond(booking.phone_number != "", booking.phone_number, "N/A") + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3ETotal Paid%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold;color:green;font-size:1.2em'%3ERM " + booking.total_price.to_string() + "%3C/td%3E%3C/tr%3E" +
        f"%3Ctr%3E%3Ctd style='padding:10px 20px;color:#666'%3EStatus%3C/td%3E%3Ctd style='padding:10px 20px;text-align:right;font-weight:bold'%3E" + booking.status + "%3C/td%3E%3C/tr%3E" +
        
        "%3C/table%3E" +
        
        # Footer
        "%3Cdiv style='background-color:#f9fafb;padding:15px;text-align:center;font-size:12px;color:#999;border-top:1px solid #eee'%3E" +
        "Thank you for using Smart Parking App%3Cbr%3EPlease retain this ticket for your records" +
        "%3C/div%3E" +
        
        "%3C/div%3E" + # End Container
        "%3C/body%3E%3C/html%3E"
    )


def booking_card(booking: Booking) -> rx.Component:
    """Refined simple and clean booking card"""
    return rx.el.div(
        # Header with subtle background
        rx.el.div(
            rx.el.div(
                rx.el.h3(booking.lot_name, class_name="text-lg font-bold text-gray-900"),
                rx.el.p(booking.lot_location, class_name="text-sm text-gray-600"),
            ),
            rx.el.div(
                booking_status_badge(booking.status),
                payment_status_badge(booking.payment_status),
                class_name="flex gap-2"
            ),
            class_name="flex items-start justify-between p-4 bg-gray-50 border-b border-gray-100"
        ),
        
        # Main info grid
        rx.el.div(
            # Date & Time
            rx.el.div(
                rx.el.p("DATE & TIME", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2"),
                rx.el.div(
                    rx.icon("calendar", class_name="h-4 w-4 text-indigo-600 mr-2 inline"),
                    rx.el.span(booking.start_date, class_name="text-sm font-semibold text-gray-900"),
                    class_name="mb-1"
                ),
                rx.el.div(
                    rx.icon("clock", class_name="h-4 w-4 text-indigo-600 mr-2 inline"),
                    rx.el.span(f"at {booking.start_time}", class_name="text-sm text-gray-700"),
                ),
            ),
            
            # Slot - Highlighted
            rx.el.div(
                rx.el.p("SLOT", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 text-center"),
                rx.el.div(
                    rx.el.p(
                        rx.cond(booking.slot_id != "", booking.slot_id, "N/A"),
                        class_name="text-xl font-black text-indigo-600"
                    ),
                    class_name="bg-indigo-50 rounded-lg py-2 px-4 text-center border border-indigo-100"
                ),
            ),
            
            # Duration
            rx.el.div(
                rx.el.p("DURATION", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 text-right"),
                rx.el.p(f"{booking.duration_hours} Hours", class_name="text-lg font-semibold text-gray-900 text-right"),
            ),
            
            class_name="grid grid-cols-3 gap-4 p-5 border-b border-gray-100 items-center"
        ),
        
        # Additional details
        rx.el.div(
            rx.el.div(
                rx.el.p("VEHICLE", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1"),
                rx.el.p(
                    rx.cond(booking.vehicle_number != "", booking.vehicle_number, "N/A"),
                    class_name="text-sm font-mono font-semibold text-gray-900"
                ),
            ),
            rx.el.div(
                rx.el.p("CONTACT", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1"),
                rx.el.p(
                    rx.cond(booking.phone_number != "", booking.phone_number, "N/A"),
                    class_name="text-sm font-medium text-gray-900"
                ),
            ),
            rx.el.div(
                rx.el.p("BOOKING ID", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1"),
                rx.el.p(booking.id, class_name="text-sm font-mono font-semibold text-gray-500"),
            ),
            class_name="grid grid-cols-3 gap-4 p-5 border-b border-gray-100 bg-white"
        ),
        
        # QR Code Section
        rx.el.div(
            rx.el.div(
                rx.el.p("SCAN QR CODE", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2"),
                rx.el.p("Present this at parking entrance", class_name="text-xs text-gray-500 mb-3"),
            ),
            # Show loader while generating, QR code when ready
            rx.cond(
                BookingState.is_generating_qr | (BookingState.qr_codes[booking.id] == ""),
                # Loader
                rx.el.div(
                    rx.spinner(
                        size="3",
                        class_name="text-indigo-600"
                    ),
                    rx.el.p(
                        "Generating QR...",
                        class_name="text-xs text-gray-500 mt-2"
                    ),
                    class_name="w-32 h-32 flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg bg-gray-50"
                ),
                # QR Code
                rx.image(
                    src=BookingState.qr_codes[booking.id],
                    alt="Booking QR Code",
                    class_name="w-32 h-32 border-2 border-gray-200 rounded-lg p-2 bg-white animate-fade-in"
                ),
            ),
            class_name="flex items-center gap-4 p-5 border-b border-gray-100 bg-gray-50"
        ),

        
        # Total and actions

        rx.el.div(
            rx.el.div(
                rx.el.p("TOTAL PAID", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1"),
                rx.el.p(f"RM {booking.total_price}", class_name="text-2xl font-bold text-green-600"),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("printer", class_name="h-4 w-4 mr-2"),
                    "Print",
                    on_click=BookingState.print_ticket(booking.id),
                    class_name="flex items-center text-sm font-medium text-gray-700 hover:text-indigo-600 bg-white hover:bg-gray-50 border border-gray-200 px-4 py-2 rounded-lg transition-colors shadow-sm"
                ),
                rx.el.button(
                    rx.icon("share-2", class_name="h-4 w-4 mr-2"),
                    "Share",
                    on_click=BookingState.share_ticket(booking.id),
                    class_name="flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 bg-white hover:bg-gray-50 border border-gray-200 px-4 py-2 rounded-lg transition-colors shadow-sm"
                ),
                rx.cond(
                    booking.status == "Confirmed",
                    rx.el.button(
                        rx.icon("x-circle", class_name="h-4 w-4 mr-2"),
                        "Cancel",
                        on_click=BookingState.initiate_cancellation(booking),
                        class_name="flex items-center text-sm font-medium text-red-600 hover:text-red-700 bg-white hover:bg-red-50 border border-red-200 px-4 py-2 rounded-lg transition-colors shadow-sm"
                    ),
                ),
                class_name="flex gap-2"
            ),
            class_name="flex items-center justify-between p-5 bg-gray-50 rounded-b-lg"
        ),
        
        class_name="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200",
        key=booking.id,
    )


def empty_state(title: str, message: str, show_cta: bool = True) -> rx.Component:
    """Enhanced empty state with better design"""
    return rx.el.div(
        rx.el.div(
            # Icon
            rx.el.div(
                rx.icon("calendar-x", class_name="w-20 h-20 text-gray-300"),
                class_name="mb-6"
            ),
            
            # Title
            rx.el.h3(
                title,
                class_name="text-2xl font-bold text-gray-900 mb-3"
            ),
            
            # Message
            rx.el.p(
                message,
                class_name="text-gray-600 mb-8 max-w-md mx-auto text-lg"
            ),
            
            # Actions
            rx.cond(
                show_cta,
                rx.el.div(
                    rx.el.a(
                        rx.icon("search", class_name="w-5 h-5 mr-2"),
                        "Browse Parking Lots",
                        href="/listings",
                        class_name="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 shadow-md hover:shadow-lg transition-all"
                    ),
                    rx.el.a(
                        "How It Works →",
                        href="/how-it-works",
                        class_name="inline-block px-6 py-3 text-indigo-600 font-semibold hover:underline ml-4"
                    ),
                    class_name="flex gap-4 justify-center"
                ),
            ),
            
            class_name="flex flex-col items-center justify-center py-20 text-center"
        ),
        class_name="bg-gray-50 rounded-xl border-2 border-dashed border-gray-300"
    )



def bookings_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.main(
            # Header
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "My Bookings",
                        class_name="text-3xl font-bold text-gray-900 mb-2"
                    ),
                    rx.el.p(
                        "Manage your parking reservations",
                        class_name="text-gray-600"
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
                ),
                class_name="bg-white border-b border-gray-200"
            ),
            
            # Tabs
            rx.el.div(
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger(
                            "Active",
                            value="active",
                            class_name="px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:text-gray-900 data-[state=active]:border-b-2 data-[state=active]:border-gray-900"
                        ),
                        rx.tabs.trigger(
                            "Past",
                            value="past",
                            class_name="px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:text-gray-900 data-[state=active]:border-b-2 data-[state=active]:border-gray-900"
                        ),
                        rx.tabs.trigger(
                            "Cancelled",
                            value="cancelled",
                            class_name="px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:text-gray-900 data-[state=active]:border-b-2 data-[state=active]:border-gray-900"
                        ),
                        class_name="flex gap-6 border-b border-gray-200 mb-8"
                    ),
                    
                    rx.tabs.content(
                        rx.cond(
                            BookingState.active_bookings.length() > 0,
                            rx.el.div(
                                rx.foreach(BookingState.active_bookings, booking_card),
                                class_name="grid grid-cols-1 md:grid-cols-2 gap-6"
                            ),
                            empty_state(
                                "No Active Bookings",
                                "You don't have any active parking reservations"
                            ),
                        ),
                        value="active",
                    ),
                    
                    rx.tabs.content(
                        rx.cond(
                            BookingState.past_bookings.length() > 0,
                            rx.el.div(
                                rx.foreach(BookingState.past_bookings, booking_card),
                                class_name="grid grid-cols-1 md:grid-cols-2 gap-6"
                            ),
                            empty_state(
                                "No Past Bookings",
                                "You haven't completed any parking reservations yet"
                            ),
                        ),
                        value="past",
                    ),
                    
                    rx.tabs.content(
                        rx.cond(
                            BookingState.cancelled_bookings.length() > 0,
                            rx.el.div(
                                rx.foreach(BookingState.cancelled_bookings, booking_card),
                                class_name="grid grid-cols-1 md:grid-cols-2 gap-6"
                            ),
                            empty_state(
                                "No Cancelled Bookings",
                                "You haven't cancelled any reservations"
                            ),
                        ),
                        value="cancelled",
                    ),
                    
                    default_value="active",
                ),
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24"
            ),
            
            class_name="flex-1 bg-gray-50"
        ),
        
        cancellation_modal(),
        footer(),
        
        class_name="font-['Roboto'] min-h-screen flex flex-col",
        on_mount=[
            AuthState.check_login,
            BookingState.generate_qr_codes,  # Generate QR codes on page load
            rx.call_script(TICKET_JS),  # Inject JavaScript on page load
        ],
    )


