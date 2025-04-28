import os
from typing import Type, Optional
import easyocr
from pydantic import BaseModel, Field
from PIL import Image
import pdf2image

from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent_execution import AgentExecution
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper

class ScanDocumentSchema(BaseModel):
    """Input for OCR Scan Document Tool."""
    file_name: str = Field(..., description="Path of the document (image/pdf) to scan")

class ScanDocumentTool(BaseTool):
    """
    Scan Document tool with EasyOCR.
    """
    name: str = "Scan Document"
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = ScanDocumentSchema
    description: str = "Scans documents (images or PDFs) and extracts text using EasyOCR"

    def _execute(self, file_name: str):
        final_path = ResourceHelper.get_agent_read_resource_path(
            file_name,
            agent=Agent.get_agent_from_id(session=self.toolkit_config.session, agent_id=self.agent_id),
            agent_execution=AgentExecution.get_agent_execution_from_id(session=self.toolkit_config.session, agent_execution_id=self.agent_execution_id)
        )

        if final_path is None:
            raise FileNotFoundError(f"File '{file_name}' not found.")

        temporary_file_path = None

        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            if final_path.lower().endswith('.txt'):
                return S3Helper().read_from_s3(final_path)
            else:
                save_directory = "/tmp"
                temporary_file_path = os.path.join(save_directory, os.path.basename(file_name))
                with open(temporary_file_path, "wb") as f:
                    contents = S3Helper().read_binary_from_s3(final_path)
                    f.write(contents)

        if temporary_file_path:
            final_path = temporary_file_path

        if not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found at {final_path}")

        reader = easyocr.Reader(['en'])

        if final_path.lower().endswith('.pdf'):
            images = pdf2image.convert_from_path(final_path)
            text = ""
            for image in images:
                results = reader.readtext(image, detail=0)
                text += " ".join(results) + "\n"
        elif final_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            image = Image.open(final_path)
            results = reader.readtext(image, detail=0)
            text = " ".join(results)
        else:
            text = self._process_other_file_types(final_path)

        if temporary_file_path:
            os.remove(temporary_file_path)

        return text

    def _process_other_file_types(self, file_path: str) -> str:
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        return "Unsupported file format."
