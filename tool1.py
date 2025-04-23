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
        # Set file path to the specific document
        file_directory = r"D:\SuperAGI"  # Directory where the files are located
        final_path = os.path.join(file_directory, file_name)  # Combine directory and file name

        # Check if the file exists
        if not os.path.exists(final_path):
            raise FileNotFoundError(f"File '{file_name}' not found at {final_path}")

        # Temporary file path if needed for S3 or other storage (if applicable)
        temporary_file_path = None
        final_name = final_path.split('/')[-1]

        # Handling files stored in S3
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            if final_path.split('/')[-1].lower().endswith('.txt'):
                return S3Helper().read_from_s3(final_path)
            else:
                save_directory = "/"
                temporary_file_path = save_directory + file_name
                with open(temporary_file_path, "wb") as f:
                    contents = S3Helper().read_binary_from_s3(final_path)
                    f.write(contents)

        # If the file doesn't exist or is not found
        if not os.path.exists(final_path) and temporary_file_path is None:
            raise FileNotFoundError(f"File '{file_name}' not found at {final_path}")

        # Set directory and create if not exists
        directory = os.path.dirname(final_path)
        os.makedirs(directory, exist_ok=True)

        if temporary_file_path is not None:
            final_path = temporary_file_path

        # Extract text from images using EasyOCR
        reader = easyocr.Reader(['en'])
        text = ""

        # Process PDF, PNG, and JPG files
        if final_path.lower().endswith('.pdf'):
            # Convert PDF to images and extract text from each page
            images = pdf2image.convert_from_path(final_path)
            for image in images:
                text += reader.readtext(image)
        elif final_path.lower().endswith('.jpg') or final_path.lower().endswith('.jpeg') or final_path.lower().endswith('.png'):
            # Perform OCR directly on image files
            image = Image.open(final_path)
            text += reader.readtext(image)
        else:
            # For other formats (epub, txt, csv, etc.), process them if needed
            text = self._process_other_file_types(final_path)

        # Remove temporary file if it was used
        if temporary_file_path is not None:
            os.remove(temporary_file_path)

        return text

    def _process_other_file_types(self, file_path: str):
        """
        Process other types of files like .epub, .csv, etc.

        Args:
            file_path (str): Path to the file to process.

        Returns:
            str: Extracted text from the file.
        """
        if file_path.lower().endswith('.epub'):
            # Process .epub files
            return self._process_epub(file_path)
        elif file_path.lower().endswith('.csv'):
            # Handle CSV files, example: correcting encoding
            return self._process_csv(file_path)
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r') as file:
                return file.read()
        return "Unsupported file type."

    def _process_epub(self, file_path: str):
        """Process .epub files and extract text."""
        from ebooklib import epub
        from bs4 import BeautifulSoup

        book = epub.read_epub(file_path)
        content = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            content.append(soup.get_text())
        return "\n".join(content)

    def _process_csv(self, file_path: str):
        """Handle CSV files."""
        from superagi.helper.validate_csv import correct_csv_encoding
        correct_csv_encoding(file_path)
        return f"CSV file content at {file_path}"  # Example placeholder
