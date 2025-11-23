"""
ADK Version: 1.18.0
This script defines two agents:

1. image_loader_agent  -> Uses a FunctionTool to "load" an image from a URL.
2. image_description_agent -> Receives the image and generates a description.

The function `load_image_api(url)` simulates calling an external API
to fetch the bytes of an image. Replace the stub with your actual API call as needed.
"""

from google.adk import Agent, FunctionTool
import base64
import requests

from google.genai import types

from google.adk.models import LlmResponse

from google.adk import Runner

# ------------------------------
# FUNCTION TOOL
# ------------------------------
def load_image_api(image_url: str) -> str:
    """
    Loads an image from a URL and returns a base64 string.
    ADK requires return types to be JSON-serializable, therefore we return str.

    Args:
        image_url (str): Public URL of the image.

    Returns:
        str: base64 string representation of the image.
    """
    response = requests.get(image_url)
    response.raise_for_status()

    # Convert image -> base64 string
    encoded = base64.b64encode(response.content).decode("utf-8")
    return encoded


# Register tool into ADK
load_image_tool = FunctionTool(
    load_image_api,
    name="load_image_api",
    description="Loads an image from a public URL and returns its base64 representation."
)

# ------------------------------
# AGENT 1: loads image via FunctionTool
# ------------------------------
image_loader_agent = Agent(
    name="Image Loader Agent",
    instructions="You receive an image URL. Use the tool to load it.",
    tools=[load_image_tool]
)

# ------------------------------
# AGENT 2: describes the image
# ------------------------------
image_description_agent = Agent(
    name="Image Description Agent",
    instructions=(
        "You receive a base64 encoded image. "
        "Give detailed description and context of what the image represents."
    )
)

# ------------------------------
# PIPELINE EXECUTION FUNCTION
# ------------------------------
def run_pipeline(image_url: str) -> str:
    """
    Runs the image processing pipeline:
      1. Image Loader Agent → loads the image
      2. Image Description Agent → describes the image

    Args:
        image_url (str): URL of the image.

    Returns:
        str: Final description returned by Agent 2
    """

    # Step 1: Agent A loads the image
    tool_result = image_loader_agent.run(
        prompt=f"Load this image: {image_url}"
    )

    # The result is base64 image string
    base64_image = tool_result.final_output

    # Step 2: Agent B describes the image content
    result = image_description_agent.run(
        prompt=f"Describe this base64 image: {base64_image}"
    )

    return result.final_output


if __name__ == "__main__":
    # Example run
    URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Fronalpstock_big.jpg/2560px-Fronalpstock_big.jpg"
    print(run_pipeline(URL))
