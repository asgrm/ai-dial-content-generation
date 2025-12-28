import asyncio
from datetime import datetime

from task._models.custom_content import Attachment
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role

class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"

async def _save_images(attachments: list[Attachment]):
    # TODO:

    #  1. Create DIAL bucket client
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as bucket_client:
    #  2. Iterate through Images from attachments, download them and then save here
        # for attachment in attachments:
        for idx, attachment in enumerate(attachments, start=1):
            ts = datetime.now().strftime(f'%Y-%m-%dT-%H-%M-%S_{idx}')
    # 3. Check if attachment is image: if attachment.type and attachment.type == 'image/png':
            if attachment.type and attachment.type == 'image/png':
    #  4. Download image: image_data = await bucket_client.get_file(attachment.url) (returns bytes)
                image_data = await bucket_client.get_file(attachment.url)
    #  5. Create filename: filename = f"{datetime.now()}.png"
                title = attachment.title or "default_title"
                filename = f"{title}_{ts}.png"
    #  6. Save image to file:
    #    - with open(filename, 'wb') as f:
    #    - f.write(image_data)

                with open(filename, 'wb') as f:
                    f.write(image_data)
    #  7. Print confirmation: print(f"Image saved: {filename}")
            print(f"Image saved: {filename}")

def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    dalle_client=DialModelClient(
        api_key=API_KEY,
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name='dall-e-3',
        # deployment_name="imagegeneration@005"
    )
    #  2. Set user input:
    #    - user_input = 'Sunny day on Bali' (or whatever you want to generate)
    user_input = 'Sunny day on Bali'
    #  3. Generate image: ai_message = dalle_client.get_completion(
    #                           messages=[Message(role=Role.USER, content=user_input)]
    #                     )
    custom_fields = {
        "size": Size.square,
        "style": Style.natural,
        "quality": Quality.standard,
    }

    # for `imagegeneration@005`` flow custom_fields are FORBIDDEN!
    ai_message = dalle_client.get_completion(
        messages=[Message(role=Role.USER, content=user_input)],
        custom_fields=custom_fields
    )
    #  3. Get attachments from response and save generated message (use method `_save_images`)
    if custom_content := ai_message.custom_content:
        if attachments := custom_content.attachments:
            print("got attachments to save")
            asyncio.run(_save_images(attachments))

    #  4. Try to configure the picture for output via `custom_fields` parameter.
    #    - Documentation: See `custom_fields`. https://dialx.ai/dial_api#operation/sendChatCompletionRequest
    #  5. Test it with the 'imagegeneration@005' (Google image generation model)


start()
