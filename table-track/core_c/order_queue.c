#include <stdio.h>
#include <stdlib.h>
#include "core.h"

// Simple Queue Node
typedef struct Node {
    int order_id;
    struct Node* next;
} Node;

typedef struct Queue {
    Node* front;
    Node* rear;
    int size;
} Queue;

static Queue regular_queue = {NULL, NULL, 0};
static Queue vip_queue = {NULL, NULL, 0};

// Internal helper
Node* create_node(int order_id) {
    Node* n = (Node*)malloc(sizeof(Node));
    n->order_id = order_id;
    n->next = NULL;
    return n;
}

void init_order_queues() {
    regular_queue.front = regular_queue.rear = NULL;
    vip_queue.front = vip_queue.rear = NULL;
    regular_queue.size = vip_queue.size = 0;
}

void enqueue_order(int order_id, int is_vip) {
    Queue* q = is_vip ? &vip_queue : &regular_queue;
    Node* n = create_node(order_id);
    if (q->rear == NULL) {
        q->front = q->rear = n;
    } else {
        q->rear->next = n;
        q->rear = n;
    }
    q->size++;
}

int dequeue_next_order() {
    // VIP has priority
    if (vip_queue.front != NULL) {
        Node* temp = vip_queue.front;
        int id = temp->order_id;
        vip_queue.front = vip_queue.front->next;
        if (vip_queue.front == NULL) vip_queue.rear = NULL;
        free(temp);
        vip_queue.size--;
        return id;
    } else if (regular_queue.front != NULL) {
        Node* temp = regular_queue.front;
        int id = temp->order_id;
        regular_queue.front = regular_queue.front->next;
        if (regular_queue.front == NULL) regular_queue.rear = NULL;
        free(temp);
        regular_queue.size--;
        return id;
    }
    return -1; // empty
}

int get_next_order_id() {
    if (vip_queue.front) return vip_queue.front->order_id;
    if (regular_queue.front) return regular_queue.front->order_id;
    return -1;
}

int get_regular_queue_size() { return regular_queue.size; }
int get_vip_queue_size() { return vip_queue.size; }