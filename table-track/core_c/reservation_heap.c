#include <stdio.h>
#include <stdlib.h>
#include "core.h"

#define MAX_RESERVATIONS 1000

typedef struct {
    int reservation_id;
    long timestamp; // Unix time
} HeapItem;

static HeapItem heap[MAX_RESERVATIONS];
static int heap_size = 0;

void init_reservation_heap() {
    heap_size = 0;
}

void sift_up(int idx) {
    while (idx > 0) {
        int parent = (idx - 1) / 2;
        if (heap[idx].timestamp >= heap[parent].timestamp) break;
        // swap
        HeapItem temp = heap[idx];
        heap[idx] = heap[parent];
        heap[parent] = temp;
        idx = parent;
    }
}

void sift_down(int idx) {
    while (1) {
        int left = 2 * idx + 1;
        int right = 2 * idx + 2;
        int smallest = idx;

        if (left < heap_size && heap[left].timestamp < heap[smallest].timestamp)
            smallest = left;
        if (right < heap_size && heap[right].timestamp < heap[smallest].timestamp)
            smallest = right;
        if (smallest == idx) break;

        HeapItem temp = heap[idx];
        heap[idx] = heap[smallest];
        heap[smallest] = temp;
        idx = smallest;
    }
}

void schedule_reservation(int reservation_id, long timestamp) {
    if (heap_size >= MAX_RESERVATIONS) return;
    heap[heap_size].reservation_id = reservation_id;
    heap[heap_size].timestamp = timestamp;
    sift_up(heap_size);
    heap_size++;
}

int get_earliest_reservation() {
    if (heap_size == 0) return -1;
    int id = heap[0].reservation_id;
    heap[0] = heap[heap_size - 1];
    heap_size--;
    if (heap_size > 0) sift_down(0);
    return id;
}

int get_heap_size() {
    return heap_size;
}