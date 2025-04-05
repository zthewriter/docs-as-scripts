import yaml
import json

def generate_openapi_schema(endpoint_title, endpoint_description, endpoint_path, http_method, request_example, response_example, response_content_type, is_part_of_collection):
    # Schema generator without field-level examples
    def json_to_schema_properties(json_data):
        properties = {}
        for key, value in json_data.items():
            if isinstance(value, str):
                properties[key] = {"type": "string", "description": f"A string field for {key}"}
            elif isinstance(value, int):
                properties[key] = {"type": "integer", "description": f"An integer field for {key}"}
            elif isinstance(value, float):
                properties[key] = {"type": "number", "description": f"A number field for {key}"}
            elif isinstance(value, bool):
                properties[key] = {"type": "boolean", "description": f"A boolean field for {key}"}
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    properties[key] = {
                        "type": "array",
                        "description": f"An array of objects for {key}",
                        "items": {"type": "object", "properties": json_to_schema_properties(value[0])}
                    }
                else:
                    properties[key] = {
                        "type": "array",
                        "description": f"An array of strings for {key}",
                        "items": {"type": "string"}
                    }
            elif isinstance(value, dict):
                properties[key] = {
                    "type": "object",
                    "description": f"An object field for {key}",
                    "properties": json_to_schema_properties(value)
                }
        return properties

    # Determine response content type and example
    def get_response_details(response_example, user_specified_type):
        # Predefined examples
        examples = {
            "image/png": "https://s3.example.com/generic-image.png",
            "application/json": {"message": "Success"},
            "text/html": "<html>Hello World!</html>",
            "text/plain": "Hello world! Welcome to our API!"
        }
        
        # Content type determination
        if user_specified_type:
            content_type = user_specified_type.lower()
            if "image/" in content_type:
                return "image/png", examples["image/png"]
            if "json" in content_type:
                return "application/json", examples["application/json"]
            if "html" in content_type:
                return "text/html", examples["text/html"]
            return content_type, examples.get(content_type, response_example)
        
        # Auto-detection from example
        if isinstance(response_example, (dict, list)):
            return "application/json", examples["application/json"]
        if isinstance(response_example, str):
            response_lower = response_example.lower()
            if "<html" in response_lower:
                return "text/html", examples["text/html"]
            if any(x in response_lower for x in [".jpg", ".png", ".gif", "image"]):
                return "image/png", examples["image/png"]
            return "text/plain", examples["text/plain"]
        
        return "text/plain", examples["text/plain"]

    # Process response details
    response_content_type, response_example = get_response_details(response_example, response_content_type)

    # Determine request body content type
    request_content_type = None
    if isinstance(request_example, dict):
        request_content_type = "application/json"
    elif isinstance(request_example, str):
        if "<html" in request_example.lower():
            request_content_type = "text/html"
        else:
            request_content_type = "text/plain"

    # Build endpoint path
    full_endpoint_path = f"/v1/{{collection}}/{endpoint_path}" if is_part_of_collection == "Yes" else f"/v1/{endpoint_path}"

    # Construct OpenAPI template
    openapi_template = {
        "openapi": "3.0.0",
        "info": {
            "title": endpoint_title,
            "description": endpoint_description,
            "version": "1.0.0"
        },
        "servers": [{"url": "https://api.example.com", "description": "Base URL for the API"}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "Enter your API Key as Bearer token"
                }
            }
        },
        "paths": {
            full_endpoint_path: {
                http_method.lower(): {
                    "summary": endpoint_title,
                    "description": endpoint_description,
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "collection",
                            "in": "path",
                            "required": True,
                            "description": "The collection ID or name",
                            "schema": {"type": "string"}
                        }
                    ] if is_part_of_collection == "Yes" else [],
                    "requestBody": {
                        "required": True,
                        "description": "Request body for the endpoint",
                        "content": {
                            request_content_type: {
                                "schema": {
                                    "type": "object" if request_content_type == "application/json" else "string",
                                    **({"properties": json_to_schema_properties(request_example)} 
                                       if request_content_type == "application/json" else {})
                                },
                                "example": request_example
                            }
                        }
                    } if http_method not in ["GET", "DELETE"] and request_example and request_content_type else {},
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                response_content_type: {
                                    "schema": {
                                        "type": "object" if isinstance(response_example, dict) else 
                                                "array" if isinstance(response_example, list) else 
                                                "string"
                                    },
                                    "example": response_example
                                }
                            }
                        },
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "403": {"description": "Forbidden"},
                        "500": {"description": "Internal Server Error"}
                    }
                }
            }
        }
    }

    return yaml.dump(openapi_template, sort_keys=False)

def main():
    # Input fields with default values
    endpoint_title = "Get User Info"
    endpoint_description = "Retrieves user information."
    endpoint_path = "users/{userId}"
    http_method = "GET"
    response_content_type = ""
    is_part_of_collection = "No"
    request_example_json = ""
    response_example_json = ""

    # You can modify these values directly or get them from user input in your preferred way
    # For example, you could use input() for command line input:
    # endpoint_title = input("Endpoint Title [Get User Info]: ") or "Get User Info"
    # endpoint_description = input("Endpoint Description [Retrieves user information.]: ") or "Retrieves user information."
    # etc.

    try:
        # Parse examples
        request_example = None
        if request_example_json.strip():
            try:
                request_example = json.loads(request_example_json)
            except json.JSONDecodeError:
                request_example = request_example_json.strip()

        response_example = None
        if response_example_json.strip():
            try:
                response_example = json.loads(response_example_json)
            except json.JSONDecodeError:
                response_example = response_example_json.strip()

        # Generate schema
        openapi_schema = generate_openapi_schema(
            endpoint_title,
            endpoint_description,
            endpoint_path,
            http_method,
            request_example,
            response_example,
            response_content_type,
            is_part_of_collection
        )

        # Output results
        print("\nGenerated OpenAPI Schema:\n")
        print(openapi_schema)
        
        # Optionally save to file
        with open("openapi_schema.yaml", "w") as f:
            f.write(openapi_schema)
        print("\nSchema saved to openapi_schema.yaml")
        
    except Exception as e:
        print(f"Error generating schema: {str(e)}")

if __name__ == "__main__":
    main()