import os
from typing import Type, Optional
import easyocr
from pydantic import BaseModel, Field
from superagi.helper.resource_helper import ResourceHelper
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution

class EasyOCRInput(BaseModel):
    image_path: str = Field(..., description="Path to the image file for OCR")

class EasyOCRTool(BaseTool):
    name: str = "EasyOCR Tool"
    description: str = "Performs OCR on an image using EasyOCR"
    
    args_schema: Type[BaseModel] = EasyOCRInput

    def _execute(self, file_name: str = None) -> str:
        """
        This method will read the image file and extract text using EasyOCR.
        The file path is generated using the ResourceHelper to ensure correct agent-level path.
        """
        # Fetch agent and agent execution details
        # Replace this with actual fetching logic for agent and execution if necessary
        agent = Agent.get_agent_from_id(session=self.toolkit_config.session, agent_id=1)  # Example agent ID
        agent_execution = AgentExecution.get_agent_execution_from_id(session=self.toolkit_config.session, agent_execution_id=1)  # Example execution ID

        # Generate the final path for the file
        final_path = ResourceHelper.get_agent_read_resource_path(file_name, agent=agent, agent_execution=agent_execution)

        # Ensure the file exists
        if not os.path.exists(final_path):
            raise FileNotFoundError(f"File not found at {final_path}")

        # Perform OCR using EasyOCR
        reader = easyocr.Reader(['en'])
        result = reader.readtext(final_path)

        # Extract text from OCR result
        text = ' '.join([item[1] for item in result])  # Extracted text

        return text
