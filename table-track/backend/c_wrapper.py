from ctypes import cdll, c_int, c_float, c_long, c_char_p, POINTER, c_bool
import os

# Load C shared library
lib_path = os.path.join(os.path.dirname(__file__), '..', 'core_c', 'core.so')
lib = cdll.LoadLibrary(lib_path)

# --- Initialization ---
lib.init_order_queues()
lib.init_reservation_heap()
lib.init_food_status_map()

# --- Order Queue ---
lib.enqueue_order.argtypes = [c_int, c_int]
lib.dequeue_next_order.restype = c_int
lib.get_next_order_id.restype = c_int
lib.get_vip_upgrade_fee.restype = c_float
lib.get_table_reservation_fee.argtypes = [c_int]
lib.get_table_reservation_fee.restype = c_float

# --- Reservation Heap ---
lib.schedule_reservation.argtypes = [c_int, c_long]
lib.get_earliest_reservation.restype = c_int

# --- Food Status ---
lib.set_order_status.argtypes = [c_int, c_int]
lib.get_order_status.argtypes = [c_int]
lib.get_order_status.restype = c_int

# --- Billing ---
lib.calculate_food_total.argtypes = [POINTER(c_float), POINTER(c_int), c_int]
lib.calculate_food_total.restype = c_float
lib.get_vip_upgrade_fee.restype = c_float
lib.get_table_reservation_fee.argtypes = [c_int]
lib.get_table_reservation_fee.restype = c_float
lib.generate_total_bill.argtypes = [c_float, c_float, c_int]
lib.generate_total_bill.restype = c_float

# Python-friendly wrappers
def enqueue_order(order_id: int, is_vip: bool):
    lib.enqueue_order(order_id, int(is_vip))

def set_order_status(order_id: int, status: int):
    lib.set_order_status(order_id, status)

def get_order_status(order_id: int) -> int:
    return lib.get_order_status(order_id)

def schedule_reservation(res_id: int, timestamp: int):
    lib.schedule_reservation(res_id, timestamp)

def calculate_total_bill(food_prices, quantities, is_premium_slot: bool, include_vip_fee: bool) -> float:
    n = len(food_prices)
    if n == 0:
        food_total = 0.0
    else:
        c_prices = (c_float * n)(*food_prices)
        c_quantities = (c_int * n)(*quantities)
        food_total = lib.calculate_food_total(c_prices, c_quantities, n)
    
    reservation_fee = lib.get_table_reservation_fee(int(is_premium_slot))
    total = lib.generate_total_bill(food_total, reservation_fee, int(include_vip_fee))
    return round(total, 2)