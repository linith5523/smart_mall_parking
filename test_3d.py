from parking_3d import create_parking_3d


figure = create_parking_3d()

figure.write_html(
    "parking_3d_test.html"
)

print(
    "3D parking visualization created successfully!"
)