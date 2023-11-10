import httpx
from PIL import Image, ImageOps, ImageDraw, ImageSequence
import io
import requests
import numpy as np

MASK_CIRCULAR = "./img/mask_circular.png"


def load_img_from_url(url) -> Image.Image:
    img_data = requests.get(url).content
    return Image.open(io.BytesIO(img_data)).convert("RGBA")


async def async_load_img_from_url(url) -> Image.Image:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

        return Image.open(io.BytesIO(resp.content)).convert("RGBA")


def cropping_image_in_a_circular(img: Image.Image) -> Image.Image:
    mask_ = Image.open(MASK_CIRCULAR).convert('L')
    return cropping_image_mask(img, mask_)


def cropping_image_mask(img: Image.Image, mask: Image.Image) -> Image.Image:
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    return output


def cropping_image_in_a_rounded_rectangle(img: Image.Image, radius=10) -> Image.Image:
    mask = Image.new("L", img.size, "black")
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), fill="white", radius=radius)

    return cropping_image_mask(img, mask)


def remove_background(img: Image.Image) -> Image.Image:
    img = img.convert('RGBA')

    data = np.array(img)
    # just use the rgb values for comparison
    rgb = data[:, :, :3]
    color = [0, 0, 0]  # Original value
    black = [0, 0, 0, 0]
    mask = np.all(rgb == color, axis=-1)
    # change all pixels that match color to white
    data[mask] = black

    return Image.fromarray(data)


def open_gif_image(path) -> list[Image.Image]:
    img = []
    with Image.open(path) as im:

        try:
            while 1:
                img.append(im.copy())
                im.seek(im.tell() + 1)
        except EOFError:

            pass  # end of sequence

    return img