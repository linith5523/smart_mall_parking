import adsa.AVLTree;
import adsa.HeapNode;
import adsa.MinHeap;

public class Main {

    public static void main(String[] args) {

        // Check whether parking slot data was provided
        if (args.length == 0) {
            System.out.println("ERROR=NO_SLOTS");
            return;
        }

        // Create the AVL Tree
        AVLTree tree = new AVLTree();

        // Create the Min Heap
        MinHeap heap = new MinHeap(args.length);

        // Process every parking slot
        for (String item : args) {

            // Expected format:
            // SLOT_ID:DISTANCE
            String[] parts = item.split(":", 2);

            if (parts.length != 2) {
                continue;
            }

            String slotId = parts[0];

            int distance;

            try {
                distance = Integer.parseInt(parts[1]);
            }
            catch (NumberFormatException e) {
                continue;
            }

            // Add slot to AVL Tree
            tree.insert(slotId);

            // Add slot and distance to Min Heap
            heap.insert(slotId, distance);
        }

        // Get the nearest parking slot
        HeapNode nearest = heap.extractMin();

        // Check if a valid slot was found
        if (nearest == null) {
            System.out.println("ERROR=NO_VALID_SLOTS");
            return;
        }

        // Send the result back to Python
        System.out.println(
            "RECOMMENDED_SLOT=" + nearest.slotId
        );

        System.out.println(
            "DISTANCE=" + nearest.distance
        );

        // Verify the selected slot using AVL Tree
        System.out.println(
            "AVL_FOUND=" + tree.search(nearest.slotId)
        );
    }
}