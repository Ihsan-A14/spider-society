import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#'''
image_path = 'components/girl_distress.png'

def onclick(event):
    if event.xdata is not None and event.ydata is not None:
        x = int(event.xdata)
        y = int(event.ydata)
        print(f"✅ Clicked at: ({x}, {y})")
        # Optional: Print it in JSON format for copy-pasting
        print(f'   "pos": [{x}, {y}],')

img = mpimg.imread(image_path)
fig, ax = plt.subplots()
ax.imshow(img)
fig.canvas.mpl_connect('button_press_event', onclick)

print(f"🎯 Opening {image_path}...")
print("👉 Click on the image where you want the TEXT or FACE to go.")
plt.show()

'''

def get_box_config(points):
    """
    Input: List of 4 (x,y) tuples: [TopLeft, TopRight, BottomLeft, BottomRight]
    Output: Prints the config dictionary for this box.
    """
    # 1. Separate X and Y values
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    
    # 2. Calculate the bounding box
    min_x = min(xs)
    min_y = min(ys)
    max_x = max(xs)
    max_y = max(ys)
    
    width = max_x - min_x
    height = max_y - min_y
    
    # 3. Print the result ready for Copy-Pasting
    print("\n✅ COPY THIS INTO YOUR CONFIG:")
    print(f'"pos": ({min_x}, {min_y}),')
    print(f'"box_size": ({width}, {height}),')
    print(f'"align": "center"')

# --- REPLACE THESE NUMBERS WITH YOUR 4 POINTS ---
# Example: Drake's Top Right Box (The "No" Box)
my_points = [
    (428, 415),  # Top Left
    (770, 415), # Top Right
    (430, 780),  # Bottom Left
    (770, 780)  # Bottom Right
]

get_box_config(my_points)

'''