#include <stdio.h>

// Configuration: these could be loaded from a config file in future
#define VIP_UPGRADE_FEE 299.0f
#define BASE_RESERVATION_FEE 0.0f      // Free by default
#define PREMIUM_RESERVATION_FEE 99.0f  // e.g., 7 PM–10 PM

// Simple helper: check if timestamp falls in premium hours (assume timestamp is Unix time)
// For demo: assume premium = 19:00 to 22:00 (7PM–10PM) in local time
// Note: Full version would use localtime() or timezone-aware logic
int is_premium_hour(long timestamp) {
    // Simplified: check if hour is between 19 and 21 (inclusive)
    // In real system, use: struct tm *ptm = localtime(&timestamp);
    // But for portability in demo, we'll simulate with modulo (not accurate, but illustrative)
    // Better: pass hour directly from Python
    return 0; // Placeholder — we’ll let Python pass is_premium flag
}

// Calculate total for food items
float calculate_food_total(float* prices, int* quantities, int count) {
    float total = 0.0f;
    for (int i = 0; i < count; i++) {
        total += prices[i] * quantities[i];
    }
    return total;
}

// Fixed VIP fee (could be dynamic later)
float get_vip_upgrade_fee() {
    return VIP_UPGRADE_FEE;
}

// Reservation fee based on time slot
float get_table_reservation_fee(int is_premium_slot) {
    return is_premium_slot ? PREMIUM_RESERVATION_FEE : BASE_RESERVATION_FEE;
}

// Generate final bill
float generate_total_bill(float food_total, float reservation_fee, int include_vip_fee) {
    float total = food_total + reservation_fee;
    if (include_vip_fee) {
        total += get_vip_upgrade_fee();
    }
    return total;
}