import base64
from pathlib import Path

from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.model_client import DialModelClient
from task._models.role import Role
from task.image_to_text.openai.message import ContentedMessage, TxtContent, ImgContent, ImgUrl


def start() -> None:
    project_root = Path(__file__).parent.parent.parent.parent
    image_path = project_root / "dialx-banner.png"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # TODO:
    #  1. Create DialModelClient
    dalle_client = DialModelClient(
        deployment_name='gpt-4o',
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        api_key=API_KEY

    )
    #  2. Call client to analise image:
    #    - try with base64 encoded format
    #    - try with URL: https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg

    data_url = "https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg"
    text_message=TxtContent(text="Explain what's in picture")
    img_content_with_url = ImgContent(image_url=ImgUrl(url=data_url))
    img_content_base64= ImgContent(image_url=ImgUrl(url=f"data:image/png;base64,{base64_image}"))

    base64_img = ContentedMessage(
        role=Role.USER,
        content=[
            text_message,
            img_content_base64
        ]
    )

    url_img = ContentedMessage(
        role=Role.USER,
        content=[
            text_message,
            img_content_with_url
        ]
    )

    # Send the inline-base64 image message to the model and print the result.
    # The DialModelClient wraps model-specific parameters under `configuration`.
    print("Sending inline base64 image")
    res_1 = dalle_client.get_completion(messages=[ base64_img])
    print("Response (inline image):", res_1)

    print("Sending url image")
    res_1 = dalle_client.get_completion(messages=[ url_img])
    print("Response (url image):", res_1)

    #  ----------------------------------------------------------------------------------------------------------------
    #  Note: This approach embeds the image directly in the message as base64 data URL! Here we follow the OpenAI
    #        Specification but since requests are going to the DIAL Core, we can use different models and DIAL Core
    #        will adapt them to format Gemini or Anthropic is using. In case if we go directly to
    #        the https://api.anthropic.com/v1/complete we need to follow Anthropic request Specification (the same for gemini)


start()