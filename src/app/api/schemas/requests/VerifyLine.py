from pydantic import BaseModel, Field

class VerifyLineRequest(BaseModel):
  file_path: str = Field(example=["/path/to/file"])

  line_number: int = Field(example=[10])