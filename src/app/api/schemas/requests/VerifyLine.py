from pydantic import BaseModel, Field

class VerifyLineRequest(BaseModel):
  host: str = Field(example=["000.000.00.00"])

  port: int = Field(example=[22])

  user: str = Field(example=["root"])

  password: str = Field(example=["password"])

  remote_file_path: str = Field(example=["/path/to/file"])

  line_number: int = Field(example=[10])