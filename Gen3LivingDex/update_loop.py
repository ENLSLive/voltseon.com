import os
from PIL import Image

def set_gifs_to_loop_once(folder_path):
    """
    Iterate through all GIFs in a folder and set them to loop only once.
    """
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    # Create an output folder for modified GIFs
    output_folder = folder_path
    os.makedirs(output_folder, exist_ok=True)

    # Process each file in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".gif"):
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                # Open the GIF
                with Image.open(input_path) as img:
                    # Save the GIF with loop=0 (no looping)
                    img.save(output_path, save_all=True, loop=None, disposal=2)
                    print(f"Processed: {filename} -> Loops set to 1")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    print(f"All GIFs processed. Modified GIFs are in '{output_folder}'.")

# Specify the folder containing GIFs
folder_with_gifs = "C:/Users/amant/Documents/GitHub/voltseon.com/Gen3LivingDex/anim"  # Replace with the actual folder path
set_gifs_to_loop_once(folder_with_gifs)
