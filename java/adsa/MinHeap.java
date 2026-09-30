package adsa;

public class MinHeap {

    private HeapNode[] heap;
    private int size;

    public MinHeap(int capacity) {
        if (capacity < 1) {
            capacity = 10;
        }

        heap = new HeapNode[capacity];
        size = 0;
    }

    // Insert a parking slot into the heap
    public void insert(String slotId, int distance) {

        ensureCapacity();

        heap[size] = new HeapNode(slotId, distance);

        int current = size;
        size++;

        // Move the new element upward
        while (current > 0) {

            int parent = (current - 1) / 2;

            if (heap[parent].distance <= heap[current].distance) {
                break;
            }

            swap(parent, current);

            current = parent;
        }
    }

    // Remove and return the nearest parking slot
    public HeapNode extractMin() {

        if (size == 0) {
            return null;
        }

        HeapNode minimum = heap[0];

        heap[0] = heap[size - 1];
        heap[size - 1] = null;
        size--;

        // Move the root downward
        heapifyDown(0);

        return minimum;
    }

    // Restore the Min Heap property
    private void heapifyDown(int index) {

        while (true) {

            int left = 2 * index + 1;
            int right = 2 * index + 2;

            int smallest = index;

            if (left < size &&
                heap[left].distance < heap[smallest].distance) {

                smallest = left;
            }

            if (right < size &&
                heap[right].distance < heap[smallest].distance) {

                smallest = right;
            }

            if (smallest == index) {
                break;
            }

            swap(index, smallest);

            index = smallest;
        }
    }

    // Swap two heap elements
    private void swap(int first, int second) {

        HeapNode temporary = heap[first];

        heap[first] = heap[second];
        heap[second] = temporary;
    }

    // Increase array size when required
    private void ensureCapacity() {

        if (size < heap.length) {
            return;
        }

        HeapNode[] newHeap = new HeapNode[heap.length * 2];

        for (int i = 0; i < heap.length; i++) {
            newHeap[i] = heap[i];
        }

        heap = newHeap;
    }

    // Check whether the heap is empty
    public boolean isEmpty() {
        return size == 0;
    }

    // Return number of elements
    public int size() {
        return size;
    }
}