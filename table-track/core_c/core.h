#ifndef CORE_H
#define CORE_H

// Order Queue (Fair + VIP)
void init_order_queues();
void enqueue_order(int order_id, int is_vip);
int dequeue_next_order();          // returns order_id
int get_next_order_id();           // peek without dequeue
int get_regular_queue_size();
int get_vip_queue_size();

// Reservation Scheduling (Min-Heap by time)
void init_reservation_heap();
void schedule_reservation(int reservation_id, long timestamp); // Unix timestamp
int get_earliest_reservation();    // returns reservation_id
int get_heap_size();

// Food Preparation Status Tracking
void init_food_status_map();
void set_order_status(int order_id, int status); // 1=Confirmed, 2=Preparing, 3=Cooking, 4=Ready
int get_order_status(int order_id);

// Billing Module
float calculate_food_total(int* item_ids, float* prices, int count);
float get_vip_upgrade_fee();
float get_table_reservation_fee(long timestamp); // e.g., premium hours cost more
float generate_total_bill(float food_total, float reservation_fee, int is_vip_upgrade);

#endif