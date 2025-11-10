#include <stdio.h>
#include <stdlib.h>
#include "core.h"

#define MAX_ORDERS 5000

static int status_map[MAX_ORDERS]; // index = order_id, value = status (1-4)

void init_food_status_map() {
    for (int i = 0; i < MAX_ORDERS; i++) {
        status_map[i] = 0; // 0 = no order
    }
}

void set_order_status(int order_id, int status) {
    if (order_id < 0 || order_id >= MAX_ORDERS) return;
    if (status < 1 || status > 4) return;
    status_map[order_id] = status;
}

int get_order_status(int order_id) {
    if (order_id < 0 || order_id >= MAX_ORDERS) return 0;
    return status_map[order_id];
}