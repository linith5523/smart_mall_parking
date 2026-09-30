package adsa;

public class AVLNode {

    public String slotId;
    public int height;

    public AVLNode left;
    public AVLNode right;

    public AVLNode(String slotId) {
        this.slotId = slotId;
        this.height = 1;
        this.left = null;
        this.right = null;
    }
}