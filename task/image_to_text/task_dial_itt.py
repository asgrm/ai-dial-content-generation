import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'
    # TODO:
    #  1. Create DialBucketClient
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as bucket_client:
    #  2. Open image file
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
    #  3. Use BytesIO to load bytes of image
        image_byte_object = BytesIO(image_bytes)
    #  4. Upload file with client
        uploaded_file = await bucket_client.put_file(name=file_name, mime_type=mime_type_png, content=image_byte_object)

        attachment = Attachment(title=file_name, url=uploaded_file.get("url"), type=mime_type_png)
    #  5. Return Attachment object with title (file name), url and type (mime type)
        return attachment


def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    # cannot use anthropic.claude-v3-haiku due to 403 access denied, used gpt-4o instead
    dial_client = DialModelClient(
        api_key=API_KEY,
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name='gpt-4o'
    )
    #  2. Upload image (use `_put_image` method )
    attachment = asyncio.run(_put_image())
    #  3. Print attachment to see result
    print(attachment)
    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])

    bucket_image_message = Message(
        role=Role.USER,
        content="What do you see on this picture?",
        custom_content=CustomContent(attachments=[attachment])
    )
    result = dial_client.get_completion(messages=[bucket_image_message])

    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis
    print(result)


start()
