package adsa;

public class AVLTree {

    private AVLNode root;

    // Get the height of a node
    private int height(AVLNode node) {
        if (node == null) {
            return 0;
        }

        return node.height;
    }

    // Get the maximum of two numbers
    private int max(int a, int b) {
        return (a > b) ? a : b;
    }

    // Calculate balance factor
    private int getBalance(AVLNode node) {
        if (node == null) {
            return 0;
        }

        return height(node.left) - height(node.right);
    }

    // Right rotation
    private AVLNode rightRotate(AVLNode y) {

        AVLNode x = y.left;
        AVLNode temporary = x.right;

        x.right = y;
        y.left = temporary;

        y.height = 1 + max(height(y.left), height(y.right));
        x.height = 1 + max(height(x.left), height(x.right));

        return x;
    }

    // Left rotation
    private AVLNode leftRotate(AVLNode x) {

        AVLNode y = x.right;
        AVLNode temporary = y.left;

        y.left = x;
        x.right = temporary;

        x.height = 1 + max(height(x.left), height(x.right));
        y.height = 1 + max(height(y.left), height(y.right));

        return y;
    }

    // Insert a parking slot
    public void insert(String slotId) {
        root = insertNode(root, slotId);
    }

    // Recursive insertion
    private AVLNode insertNode(AVLNode node, String slotId) {

        // Normal Binary Search Tree insertion
        if (node == null) {
            return new AVLNode(slotId);
        }

        if (slotId.compareTo(node.slotId) < 0) {
            node.left = insertNode(node.left, slotId);
        }
        else if (slotId.compareTo(node.slotId) > 0) {
            node.right = insertNode(node.right, slotId);
        }
        else {
            // Duplicate slot ID
            return node;
        }

        // Update height
        node.height = 1 + max(
            height(node.left),
            height(node.right)
        );

        // Calculate balance factor
        int balance = getBalance(node);

        // LL Case
        if (balance > 1 &&
            slotId.compareTo(node.left.slotId) < 0) {

            return rightRotate(node);
        }

        // RR Case
        if (balance < -1 &&
            slotId.compareTo(node.right.slotId) > 0) {

            return leftRotate(node);
        }

        // LR Case
        if (balance > 1 &&
            slotId.compareTo(node.left.slotId) > 0) {

            node.left = leftRotate(node.left);

            return rightRotate(node);
        }

        // RL Case
        if (balance < -1 &&
            slotId.compareTo(node.right.slotId) < 0) {

            node.right = rightRotate(node.right);

            return leftRotate(node);
        }

        return node;
    }

    // Search for a parking slot
    public boolean search(String slotId) {

        AVLNode current = root;

        while (current != null) {

            int comparison = slotId.compareTo(current.slotId);

            if (comparison == 0) {
                return true;
            }

            if (comparison < 0) {
                current = current.left;
            }
            else {
                current = current.right;
            }
        }

        return false;
    }
}