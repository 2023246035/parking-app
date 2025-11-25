"""
Extension to BookingState for slot selection functionality.
Add these methods and variables to app/states/booking_state.py
"""

# ADD THESE STATE VARIABLES to BookingState class (around line 37):
"""
    booking_step: int = 1  # Current step in booking wizard (1-4)
    selected_slot: str = ""  # Selected parking slot (e.g., "A5")
    vehicle_number: str = ""  # Vehicle registration number
    phone_number: str = ""  # Contact phone number
"""

# ADD THESE COMPUTED VARIABLES after line 50:
"""
    @rx.var
    def zone_a_slots(self) -> list[str]:
        '''Generate Zone A slots (A1-A10)'''
        return [f"A{i}" for i in range(1, 11)]
    
    @rx.var
    def zone_b_slots(self) -> list[str]:
        '''Generate Zone B slots (B1-B10)'''
        return [f"B{i}" for i in range(1, 11)]
    
    @rx.var
    def can_proceed_to_next_step(self) -> bool:
        '''Check if user can proceed to next step'''
        if self.booking_step == 1:
            return self.selected_slot != ""
        elif self.booking_step == 2:
            return True  # Date/time always valid with defaults
        elif self.booking_step == 3:
            return self.vehicle_number != "" and self.phone_number != ""
        return True
"""

# ADD THESE EVENT HANDLERS after line 150:
"""
    @rx.event
    def select_slot(self, slot: str):
        '''Select a parking slot'''
        self.selected_slot = slot
    
    @rx.event
    def set_vehicle_number(self, number: str):
        '''Set vehicle registration number'''
        self.vehicle_number = number.upper()
    
    @rx.event
    def set_phone_number(self, number: str):
        '''Set contact phone number'''
        self.phone_number = number
    
    @rx.event
    def next_step(self):
        '''Move to next step in booking wizard'''
        if self.can_proceed_to_next_step and self.booking_step < 4:
            self.booking_step += 1
    
    @rx.event
    def previous_step(self):
        '''Move to previous step in booking wizard'''
        if self.booking_step > 1:
            self.booking_step -= 1
    
    @rx.event
    def reset_booking_wizard(self):
        '''Reset booking wizard to step 1'''
        self.booking_step = 1
        self.selected_slot = ""
        self.vehicle_number = ""
        self.phone_number = ""
"""

# MODIFY open_modal method (line 125) to reset wizard:
"""
    @rx.event
    def open_modal(self, lot: ParkingLot):
        self.selected_lot = lot
        self.is_modal_open = True
        self.start_date = datetime.now().strftime("%Y-%m-%d")
        self.start_time = (datetime.now() + timedelta(hours=1)).strftime("%H:00")
        self.duration_hours = 2
        self.reset_booking_wizard()  # ADD THIS LINE
"""

#MODIFY process_payment method (around line 199) to save slot and vehicle info:
"""
Add these fields when creating new_booking (around line 199-210):
                slot_number=self.selected_slot,
                vehicle_number=self.vehicle_number,
                phone_number=self.phone_number,
"""
