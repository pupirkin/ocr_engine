import os
from typing import Type
import easyocr
from pydantic import BaseModel, Field
from superagi.helper.resource_helper import ResourceHelper
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from pdf2image import convert_from_path

class EasyOCRInput(BaseModel):
    file_path: str = Field(..., description="Path to the image or PDF file for OCR")

class EasyOCRTool(BaseTool):
    name: str = "EasyOCR Tool"
    description: str = "Performs OCR on an image or PDF using EasyOCR"
    args_schema: Type[BaseModel] = EasyOCRInput

    def _execute(self, file_name: str = None) -> str:
        """
        This method will read the image file (or PDF converted to images) and extract text using EasyOCR.
        The file path is generated using the ResourceHelper to ensure correct agent-level path.
        """
        agent = Agent.get_agent_from_id(session=self.toolkit_config.session, agent_id=1)
        agent_execution = AgentExecution.get_agent_execution_from_id(session=self.toolkit_config.session, agent_execution_id=1)
        
        # Generate the final path for the file
        final_path = ResourceHelper.get_agent_read_resource_path(file_name, agent=agent, agent_execution=agent_execution)

        # Ensure the file exists
        if not os.path.exists(final_path):
            raise FileNotFoundError(f"File not found at {final_path}")

        # Handle PDF file
        if final_path.endswith('.pdf'):
            # Convert PDF to images
            pages = convert_from_path(final_path)
            text = ''
            reader = easyocr.Reader(['en'])
            for page in pages:
                page_text = reader.readtext(page)
                text += ' '.join([item[1] for item in page_text]) + '\n'
            return text

        # Handle image files (JPEG, PNG)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(final_path)
        text = ' '.join([item[1] for item in result])

        return text
