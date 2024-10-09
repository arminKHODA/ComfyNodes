import os
import torch
import numpy as np
from PIL import Image
import random
from datetime import datetime

class UltraImageSave:
    def __init__(self):
        self.type = "output"
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "output_folder": ("STRING", {"default": "./output", "tooltip": "Path to save the images."}),
                "filename": ("STRING", {"default": "image", "tooltip": "Exact name for the file to save (without extension)."}),
                "format": (["png", "jpg"], {"default": "png", "tooltip": "Select the file format to save as."}),
                "overwrite": ("BOOLEAN", {"default": True, "tooltip": "If True, overwrite the file if it exists. If False, append a random seed to avoid overwriting."}),
                "string_to_replace": ("STRING", {"default": "", "tooltip": "String in the filename to replace (if any)."}),
                "replacement_string": ("STRING", {"default": "", "tooltip": "Replacement string in the filename (if any)."}),
                "delete_old_file": ("BOOLEAN", {"default": False, "tooltip": "If True, deletes the old file with the original filename after renaming."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("FileName_input", "FileName_output", "STRING")
    RETURN_NAMES = ("FileName_input", "FileName_output", "FullFilePath_output")

    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "armin"
    DESCRIPTION = "Saves the input images to the specified folder with the exact file name, allowing string replacement, overwriting, and optionally deleting the old file. Also returns the original and new filenames."


    def process_filename(self, filename):
        current_date = datetime.now().strftime("%Y%m%d")
        current_time = datetime.now().strftime("%H%M%S")
        filename = filename.replace("%date:yyyyMMdd%", current_date)
        filename = filename.replace("%date:hhmmss%", current_time)
        return filename

    def save_images(self, images, output_folder="./output", filename="image", format="png", overwrite=True,
                    string_to_replace="", replacement_string="", delete_old_file=False, prompt=None, extra_pnginfo=None):

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)


        if format not in ["jpg", "png"]:
            raise ValueError("Invalid format. Only 'jpg' and 'png' formats are supported.")

        file_format = "JPEG" if format == "jpg" else "PNG"
        original_filename = filename
        filename = self.process_filename(filename)

        if string_to_replace:
            filename = filename.replace(string_to_replace, replacement_string)

        file_path = os.path.join(output_folder, filename)

        if not overwrite and os.path.exists(f"{file_path}.{format}"):
            random_seed = random.randint(1000000000, 9999999999)
            file_path = f"{file_path}_{random_seed}"

        file_path = f"{file_path}.{format}"

        if delete_old_file and string_to_replace and original_filename != filename:
            old_file_path = os.path.join(output_folder, f"{original_filename}.{format}")
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
                print(f"Deleted old file: {old_file_path}")

        results = []
        full_file_paths = []  

        for batch_number, image in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            if format == "jpg" and img.mode == "RGBA":
                img = img.convert("RGB")

            if format == "png":
                img.save(file_path, format=file_format, compress_level=0)
            elif format == "jpg":
                img.save(file_path, format=file_format, quality=100)

            full_file_paths = file_path

            results.append({
                "filename": file_path,
                "folder": output_folder,
                "type": self.type
            })

        return original_filename, filename, full_file_paths




NODE_CLASS_MAPPINGS = {
    "UltraImageSave": UltraImageSave
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UltraImageSave": "Ultra Image Save"
}
