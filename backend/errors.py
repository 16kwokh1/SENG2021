# Relevant python libraries are imported
from werkzeug.exceptions import HTTPException

# A custom AccessError is defined here
class AccessError(HTTPException):
    code = 400
    message = 'No message specified'
