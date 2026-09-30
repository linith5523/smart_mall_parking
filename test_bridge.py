from java_bridge import get_recommended_slot


# Test parking slots
slots = [
    ("A-1-001", 50),
    ("B-1-002", 20),
    ("C-1-003", 70)
]


# Ask Java to find the nearest slot
result = get_recommended_slot(slots)


# Display the result
print("Python received:")

print(result)