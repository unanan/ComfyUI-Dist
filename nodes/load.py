# Concludes all "Load" nodes

import os
import json
import paramiko
import requests
import hashlib
import torch
from PIL import Image, ImageOps, ImageSequence
import numpy as np
from .constants import DIST_STORAGE_MACHINE_HOST, DIST_STORAGE_MACHINE_USER, DIST_STORAGE_MACHINE_COMFYUI_ROOT, DIST_STORAGE_MACHINE_PRIVATE_KEY_FILE

IMAGE_EXTS = [".jpg", ".png", ".JPEG", ".PNG"]  #TODO


def read_file(file_name):
    pkey = paramiko.RSAKey.from_private_key_file(DIST_STORAGE_MACHINE_PRIVATE_KEY_FILE)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=DIST_STORAGE_MACHINE_HOST,
        port=22,
        username=DIST_STORAGE_MACHINE_USER,
        pkey=pkey)
    sftp_client = ssh_client.open_sftp()
    remote_file = sftp_client.open(os.path.join(DIST_STORAGE_MACHINE_COMFYUI_ROOT, "input/", file_name))
    ssh_client.close()
    return remote_file


def get_input_images():
    pkey = paramiko.RSAKey.from_private_key_file(DIST_STORAGE_MACHINE_PRIVATE_KEY_FILE)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=DIST_STORAGE_MACHINE_HOST,
        port=22,
        username=DIST_STORAGE_MACHINE_USER,
        pkey=pkey)
    sftp_client = ssh_client.open_sftp()
    file_list = []
    for file_name in sftp_client.listdir(os.path.join(DIST_STORAGE_MACHINE_COMFYUI_ROOT, "input/")):
        if os.path.splitext(file_name)[-1] in IMAGE_EXTS:
            file_list.append(file_name)
    ssh_client.close()
    return file_list


#
# class LoadWorkflowFromLAN:
#     '''
#     Load workflow json file from local or other machine, only need to provide file name
#     '''
#     pass
#
#
# class LoadWorkflowFromURL:
#     '''
#     Load workflow json file from URL
#     '''
#     pass


class LoadImageFromLAN:
    '''
    Load image from other machine in the local area network, only need to provide image name
    Reference to: ComfyUI/nodes.py
    '''

    @classmethod
    def INPUT_TYPES(s):
        files = [f for f in get_input_images()]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True})},
                }

    CATEGORY = "image"

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    TITLE = "Load Image (LAN)"

    def load_image(self, image):
        img = Image.open(read_file(image))
        output_images = []
        output_masks = []
        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)
            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

    @classmethod
    def IS_CHANGED(s, image):
        fp = read_file(image)
        m = hashlib.sha256()
        m.update(fp.read())

        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image):
        try:
            read_file(image)
        except:
            return "Invalid image file: {}".format(image)

        return True


class LoadImageFromURL:
    '''
    Load image from URL
    Reference to: city96/ComfyUI_NetDist
    '''

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": ("STRING", {"multiline": False, })
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    CATEGORY = "image"
    TITLE = "Load Image (URL)"

    def load_image(self, url):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            i = Image.open(r.raw)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
        return (image, mask)


# class LoadCheckpointFromLAN:
#     '''
#     Load checkpoint from local or other machine, only need to provide file name
#     '''
#     pass
#
#
# class LoadCheckpointFromURL:
#     '''
#     Load checkpoint from URL
#     '''
#     pass


NODE_CLASS_MAPPINGS = {
    # "LoadWorkflowFromLAN": LoadWorkflowFromLAN,
    # "LoadWorkflowFromURL": LoadWorkflowFromURL,
    "LoadImageFromLAN": LoadImageFromLAN,
    "LoadImageFromURL": LoadImageFromURL,
    # "LoadCheckpointFromLAN": LoadCheckpointFromLAN,
    # "LoadCheckpointFromURL": LoadCheckpointFromURL,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # "LoadWorkflowFromLAN": "🐵 Load Workflow (From LAN)",
    # "LoadWorkflowFromURL": "🐵 Load Workflow (From URL)",
    "LoadImageFromLAN": "🐵 Load Image (From LAN)",
    "LoadImageFromURL": "🐵 Load Image (From URL)",
    # "LoadCheckpointFromLAN": "🐵 Load Checkpoint (From LAN)",
    # "LoadCheckpointFromURL": "🐵 Load Checkpoint (From URL)",
}
