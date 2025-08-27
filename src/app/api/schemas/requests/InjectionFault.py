from pydantic import BaseModel, Field

class InjectionFaultRequest(BaseModel):
    file_path: str = Field(example=["/path/to/file"])
    
    line_number: int = Field(example=[10])
    
    new_content: str = Field(example=["New line content"])
