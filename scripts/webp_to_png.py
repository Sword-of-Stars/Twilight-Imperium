from PIL import Image
import os

def convert_webp_to_png(webp_path, png_path):
    """
    Converts a WebP image to PNG format.

    Args:
        webp_path (str): Path to the input WebP image.
        png_path (str): Path to save the output PNG image.
    """
    try:
        image = Image.open(webp_path)
        image.save(png_path, "PNG")
        print(f"Converted '{webp_path}' to '{png_path}'")
    except FileNotFoundError:
        print(f"Error: File not found: {webp_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def convert_multiple_webp_to_png(directory):
  """
  Converts all WebP images in a directory to PNG format.

  Args:
      directory (str): Path to the directory containing WebP images.
  """
  for filename in os.listdir(directory):
    if filename.lower().endswith(".webp"):
      webp_path = os.path.join(directory, filename)
      png_path = os.path.join(directory, os.path.splitext(filename)[0] + ".png")
      convert_webp_to_png(webp_path, png_path)

if __name__ == "__main__":
    # Example usage:
    # 1. Convert a single WebP image:
    #convert_webp_to_png("image.webp", "image.png")

    # 2. Convert all WebP images in a directory:
    convert_multiple_webp_to_png("src/data/tiles")
    # Ensure the directory "images_directory" exists or replace with your directory path.
    pass