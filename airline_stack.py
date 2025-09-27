import datetime
import itertools

# Generate unique PNRs
_pnr_counter = itertools.count(1000)


class Flight:
    def __init__(self, code, origin, destination, rows=5, seats_per_row=4):
        self.code = code
        self.origin = origin
        self.destination = destination
        self.total_seats = rows * seats_per_row
        # seat map like 1A, 1B, ...
        self.available_seats = [
            f"{r}{chr(65+c)}" for r in range(1, rows + 1) for c in range(seats_per_row)
        ]
        self.booked_seats = {}

    def available_seat_count(self):
        return len(self.available_seats)

    def book_seat(self, seat_no=None):
        """Book a specific seat or the first available one"""
        if not self.available_seats:
            return None
        if seat_no and seat_no not in self.available_seats:
            return None
        seat = seat_no if seat_no else self.available_seats[0]
        self.available_seats.remove(seat)
        self.booked_seats[seat] = True
        return seat

    def cancel_seat(self, seat_no):
        """Cancel seat booking"""
        if seat_no in self.booked_seats:
            del self.booked_seats[seat_no]
            self.available_seats.append(seat_no)
            return True
        return False

    def __str__(self):
        return f"{self.code} | {self.origin}->{self.destination} | Available Seats: {self.available_seat_count()}/{self.total_seats}"


class Booking:
    def __init__(self, passenger_name, age, flight, seat_no):
        self.pnr = f"PNR{next(_pnr_counter)}"
        self.passenger_name = passenger_name
        self.age = age
        self.flight = flight
        self.seat_no = seat_no
        self.time = datetime.datetime.now()

    def __str__(self):
        t = self.time.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.pnr} | {self.passenger_name} ({self.age}) | Flight: {self.flight.code} | Seat: {self.seat_no} | Booked: {t}"


class AirlineStackSystem:
    def __init__(self):
        self.booking_stack = []     # LIFO for bookings
        self.cancelled_stack = []   # LIFO for cancellations
        self.flights = {}
        self._create_sample_flights()

    def _create_sample_flights(self):
        flights = [
            ("AI101", "Mumbai", "Delhi"),
            ("AI202", "Bengaluru", "Chennai"),
            ("6E303", "Kolkata", "Hyderabad"),
            ("SG404", "Pune", "Goa"),
        ]
        for code, o, d in flights:
            self.flights[code] = Flight(code, o, d, rows=3, seats_per_row=4)

    def display_flights(self):
        print("\nAvailable flights:")
        for f in self.flights.values():
            print("  -", f)

    def show_seat_map(self, flight):
        """Display available and booked seats in grid form"""
        print(f"\nSeat map for Flight {flight.code} ({flight.origin}->{flight.destination}):")
        all_seats = sorted(flight.available_seats + list(flight.booked_seats.keys()))
        for i, seat in enumerate(all_seats, 1):
            if seat in flight.available_seats:
                print(f"[{seat}]", end=" ")
            else:
                print(f"[X{seat}]", end=" ")  # X marks booked
            if i % 4 == 0:
                print()
        print()

    def make_booking(self, passenger_name, age, flight_code, seat_no=None):
        if flight_code not in self.flights:
            print("Flight code not found.")
            return None
        flight = self.flights[flight_code]
        seat = flight.book_seat(seat_no)
        if not seat:
            print("Seat not available.")
            return None
        booking = Booking(passenger_name, age, flight, seat)
        self.booking_stack.append(booking)  # push
        print(f"Booking successful: {booking.pnr}, Seat: {seat}")
        return booking

    def cancel_last_booking(self):
        if not self.booking_stack:
            print("No bookings to cancel.")
            return None
        booking = self.booking_stack.pop()  # pop
        booking.flight.cancel_seat(booking.seat_no)
        self.cancelled_stack.append(booking)
        print(f"Cancelled booking: {booking.pnr}, Seat {booking.seat_no}")
        return booking

    def undo_last_cancellation(self):
        if not self.cancelled_stack:
            print("No cancellations to undo.")
            return None
        booking = self.cancelled_stack.pop()
        seat = booking.flight.book_seat(booking.seat_no)
        if seat:
            self.booking_stack.append(booking)
            print(f"Undo cancel: Restored booking {booking.pnr}, Seat {seat}")
            return booking
        else:
            print("Seat already taken, cannot undo.")
            self.cancelled_stack.append(booking)
            return None

    def view_last_booking(self):
        if not self.booking_stack:
            print("No bookings yet.")
            return None
        booking = self.booking_stack[-1]  # peek
        print("Last booking (top of stack):")
        print(" ", booking)
        return booking

    def view_all_bookings(self):
        if not self.booking_stack:
            print("No bookings yet.")
            return []
        print("\nAll bookings (most recent first):")
        for i, b in enumerate(reversed(self.booking_stack), 1):
            print(f"{i}. {b}")
        return list(self.booking_stack)


def main_menu():
    system = AirlineStackSystem()
    while True:
        print("\n====== Airline Management (Stack-based + Seat Numbers) ======")
        print("1. Display flights")
        print("2. Show seat map for a flight")
        print("3. Make booking")
        print("4. Cancel last booking")
        print("5. Undo last cancellation")
        print("6. View last booking")
        print("7. View all bookings")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            system.display_flights()

        elif choice == "2":
            code = input("Enter flight code: ").strip().upper()
            if code in system.flights:
                system.show_seat_map(system.flights[code])
            else:
                print("Invalid flight code.")

        elif choice == "3":
            system.display_flights()
            name = input("Passenger name: ").strip()
            age = int(input("Age: ").strip())
            flight_code = input("Flight code: ").strip().upper()
            seat_no = input("Seat number (or press Enter for auto): ").strip().upper()
            seat_no = seat_no if seat_no else None
            system.make_booking(name, age, flight_code, seat_no)

        elif choice == "4":
            system.cancel_last_booking()

        elif choice == "5":
            system.undo_last_cancellation()

        elif choice == "6":
            system.view_last_booking()

        elif choice == "7":
            system.view_all_bookings()

        elif choice == "0":
            print("Exiting. Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
