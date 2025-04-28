from pydantic import BaseModel, Field
import os
from typing import Type, Optional
import easyocr
from superagi.helper.resource_helper import ResourceHelper
from superagi.models.agent_execution import AgentExecution
from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.types.storage_types import StorageType
from superagi.config.config import get_config
from PIL import Image
import pdf2image
from io import BytesIO
from superagi.helper.s3_helper import S3Helper

class ScanDocumentSchema(BaseModel):
    """Input for OCR Scan Document Tool."""
    file_name: str = Field(..., description="Path of the document (image/pdf) to scan")

class EasyOCRTool(BaseTool):
    """
    Scan Document tool with EasyOCR.
    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Scan Document"
    agent_id: int = None
    agent_execution_id: int = None
    args_schema: Type[BaseModel] = ScanDocumentSchema
    description: str = "Scans documents (images or PDFs) and extracts text using EasyOCR"

    def _execute(self, file_name: str):
        """
        Execute the scan document tool.

        Args:
            file_name : The name of the document to scan.

        Returns:
            The extracted text from the document.
        """
        # Set the final file path
        final_path = ResourceHelper.get_agent_read_resource_path(
            file_name,
            agent=Agent.get_agent_from_id(self.toolkit_config.session, self.agent_id),
            agent_execution=AgentExecution.get_agent_execution_from_id(self.toolkit_config.session, self.agent_execution_id)
        )

        temporary_file_path = None

        # Handle S3 storage
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            if final_path.lower().endswith('.txt'):
                return S3Helper().read_from_s3(final_path)
            else:
                temporary_file_path = os.path.join("/tmp", os.path.basename(file_name))
                with open(temporary_file_path, "wb") as f:
                    contents = S3Helper().read_binary_from_s3(final_path)
                    f.write(contents)

        # Check if the final path exists
        if not os.path.exists(final_path) and temporary_file_path is None:
            raise FileNotFoundError(f"File '{file_name}' not found.")

        if temporary_file_path is not None:
            final_path = temporary_file_path

        # Start OCR Reader
        reader = easyocr.Reader(['en', 'de'])  # English and German supported
        text = ""

        # Process PDFs
        if final_path.lower().endswith('.pdf'):
            images = pdf2image.convert_from_path(final_path)
            for image in images:
                result = reader.readtext(image, detail=0)  # detail=0 returns only text
                text += " ".join(result) + "\n"
        # Process images
        elif final_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            image = Image.open(final_path)
            result = reader.readtext(image, detail=0)
            text = " ".join(result)
        else:
            # Other files (txt, csv, epub)
            text = self._process_other_file_types(final_path)

        # Remove temporary file
        if temporary_file_path is not None:
            os.remove(temporary_file_path)

        return text

    def _process_other_file_types(self, file_path: str):
        """
        Process other types of files like .txt.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Extracted text.
        """
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        return "Unsupported file type."
