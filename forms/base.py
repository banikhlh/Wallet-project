# forms/base.py
from pydantic import BaseModel, validator
from typing import Optional, Any

class BaseForm(BaseModel):
    
    class Config:
        arbitrary_types_allowed = True
    
    def errors_to_dict(self) -> dict:
        errors = {}
        for error in self.errors:
            field = error['loc'][0]
            errors[field] = error['msg']
        return errors