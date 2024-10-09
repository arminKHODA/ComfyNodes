import os
import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence
import hashlib

class UltraImageLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ImageID": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
                "FolderPath": ("STRING", {"default": "./images", "tooltip": "Path to the folder containing images"}),
                "RespectSubfolders": (["off", "on"], {"default": "off", "tooltip": "Respect subfolders when loading images"}),
                "StringFilter": ("STRING", {"default": "", "tooltip": "If this string is found in the filename, load the image."}),
                "ExcludeStringFilter": ("STRING", {"default": "", "tooltip": "If this string is found in the filename, skip the image."})
            }
        }

    CATEGORY = "armin"
    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("TotalImages", "ImageFilename", "Image", "FolderPath") 
    FUNCTION = "load_image"

    def load_image(self, ImageID, FolderPath, RespectSubfolders="off", StringFilter="", ExcludeStringFilter=""):
        def find_images(folder, respect_subfolders):
            image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp') 
            images = []
            if respect_subfolders == "on":
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if file.lower().endswith(image_extensions):
                            images.append(os.path.join(root, file))
            else:
                for file in os.listdir(folder):
                    if file.lower().endswith(image_extensions):
                        images.append(os.path.join(folder, file))
            return images


        images = find_images(FolderPath, RespectSubfolders)

        
        filtered_images = []
        for image in images:
            filename = os.path.basename(image)

            
            if StringFilter and StringFilter not in filename:
                continue  

            
            if ExcludeStringFilter and ExcludeStringFilter in filename:
                continue  

            filtered_images.append(image)

        if not filtered_images:
            return ("0", "", None)  

        
        ImageID = ImageID % len(filtered_images)

        
        image_path = filtered_images[ImageID]

        
        image_filename = os.path.splitext(os.path.basename(image_path))[0]

        
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)  

        output_images = []
        w, h = None, None

        excluded_formats = ['MPO']

        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            if image.size[0] != w or image.size[1] != h:
                continue

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]  
            
            output_images.append(image)

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
        else:
            output_image = output_images[0]


        return (str(len(filtered_images)), image_filename, output_image, FolderPath)

    @classmethod
    def IS_CHANGED(s, ImageID, FolderPath, RespectSubfolders, StringFilter, ExcludeStringFilter):

        return True

    @classmethod
    def VALIDATE_INPUTS(s, ImageID, FolderPath, RespectSubfolders, StringFilter, ExcludeStringFilter):

        if not os.path.exists(FolderPath):
            return f"Invalid folder path: {FolderPath}"
        return True


NODE_CLASS_MAPPINGS = {
    "UltraImageLoader": UltraImageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UltraImageLoader": "Ultra Image Loader"
}
