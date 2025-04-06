import yaml
import json
import os
from typing import Dict, Any

CONTENT_TYPES = {
    '.json': 'application/json',
    '.html': 'text/html',
    '.txt': 'text/plain',
    '.xml': 'application/xml'
}

AUTH_TYPES = {
    '1': ('apiKey', 'API Key'),
    '2': ('http', 'HTTP Basic'),
    '3': ('oauth2', 'OAuth 2.0'),
    '4': ('openIdConnect', 'OpenID Connect'),
    'none': (None, 'None')
}

def detect_content_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return CONTENT_TYPES.get(ext, 'text/plain')

def read_example_file(filename: str) -> Any:
    try:
        with open(filename, 'r') as f:
            if filename.endswith('.json'):
                return json.load(f)
            return f.read()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def generate_schema(data: Any, content_type: str) -> Dict[str, Any]:
    if content_type != 'application/json' or not isinstance(data, dict):
        return {
            "type": "string",
            "description": f"{content_type.split('/')[-1].title()} content"
        }
    
    schema = {
        "type": "object",
        "properties": {}
    }
    
    for key, value in data.items():
        field_type = "string"
        if isinstance(value, bool):
            field_type = "boolean"
        elif isinstance(value, int):
            field_type = "integer"
        elif isinstance(value, float):
            field_type = "number"
        elif isinstance(value, list):
            field_type = "array"
        elif isinstance(value, dict):
            field_type = "object"
        
        schema["properties"][key] = {
            "type": field_type,
            "description": f"The {key.replace('_', ' ')}",
            "example": value
        }
        
        if field_type == "integer" and "id" in key.lower():
            schema["properties"][key]["format"] = "int64"
    
    return schema

def add_auth_scheme(spec: Dict[str, Any]) -> Dict[str, Any]:
    print("\n=== Authentication Setup ===")
    print("Select authentication type:")
    for num, (_, name) in AUTH_TYPES.items():
        if num != 'none':
            print(f"{num}. {name}")
    print("none. No authentication")
    
    choice = input("Your choice [none]: ").strip().lower() or "none"
    auth_type, auth_name = AUTH_TYPES.get(choice, (None, None))
    
    if not auth_type:
        return spec
    
    if 'components' not in spec:
        spec['components'] = {}
    if 'securitySchemes' not in spec['components']:
        spec['components']['securitySchemes'] = {}
    
    scheme = {"type": auth_type}
    
    if auth_type == "apiKey":
        scheme["name"] = input("Header/query parameter name [api_key]: ") or "api_key"
        scheme["in"] = input("Location (header/query/cookie) [header]: ") or "header"
        scheme["description"] = input("Description [API key authentication]: ") or "API key authentication"
    
    elif auth_type == "http":
        scheme["scheme"] = input("Scheme (basic/bearer/etc) [bearer]: ") or "bearer"
        if scheme["scheme"] == "bearer":
            scheme["bearerFormat"] = input("Bearer format (e.g. JWT) [JWT]: ") or "JWT"
        scheme["description"] = input("Description [HTTP authentication]: ") or "HTTP authentication"
    
    elif auth_type in ["oauth2", "openIdConnect"]:
        scheme["flows"] = {
            "authorizationCode": {
                "authorizationUrl": input("Authorization URL: "),
                "tokenUrl": input("Token URL: "),
                "scopes": {}
            }
        }
        while True:
            scope = input("Add scope (format: 'scope:description' or 'done'): ")
            if scope.lower() == 'done':
                break
            if ':' in scope:
                name, desc = scope.split(':', 1)
                scheme["flows"]["authorizationCode"]["scopes"][name.strip()] = desc.strip()
    
    spec['components']['securitySchemes'][f"{auth_type}Auth"] = scheme
    
    # Apply security globally
    if input("\nApply this security globally to all endpoints? (y/n) [y]: ").lower() != 'n':
        if 'security' not in spec:
            spec['security'] = []
        spec['security'].append({f"{auth_type}Auth": []})
    
    return spec

def build_openapi_spec():
    print("OpenAPI Specification Builder")
    print("=" * 40)
    
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": input("API Title: ").strip() or "My API",
            "version": input("API Version [1.0.0]: ").strip() or "1.0.0",
            "description": input("API Description (optional): ").strip() or ""
        },
        "servers": [{
            "url": input("Base URL [https://api.example.com]: ").strip() or "https://api.example.com",
            "description": "Production server"
        }],
        "paths": {}
    }
    
    # Add authentication
    spec = add_auth_scheme(spec)
    
    # Endpoint setup
    path = input("\nEndpoint path (e.g. '/pets/{id}'): ").strip()
    method = input("HTTP Method [put]: ").strip().lower() or "put"
    
    # Request Body
    request_schema = None
    request_example = None
    if method in ['post', 'put', 'patch']:
        req_file = input("Request example file (e.g. request.json): ").strip()
        if req_file and os.path.exists(req_file):
            request_content_type = detect_content_type(req_file)
            request_example = read_example_file(req_file)
            request_schema = generate_schema(request_example, request_content_type)
    
    # Response
    resp_file = input("Response example file (e.g. response.json): ").strip()
    if not resp_file or not os.path.exists(resp_file):
        print("Error: Response example file is required!")
        return
    
    response_content_type = detect_content_type(resp_file)
    response_example = read_example_file(resp_file)
    response_schema = generate_schema(response_example, response_content_type)
    
    # Build the operation
    operation = {
        "summary": f"{method.upper()} operation for {path}",
        "description": f"Perform {method.upper()} operation on {path}",
        "responses": {
            "200": {
                "description": "Successful operation",
                "content": {
                    response_content_type: {
                        "schema": response_schema,
                        "example": response_example
                    }
                }
            }
        }
    }
    
    # Add path parameters
    if "{" in path:
        path_params = [p.strip("{}") for p in path.split("/") if "{" in p]
        operation["parameters"] = [{
            "name": param,
            "in": "path",
            "required": True,
            "schema": {
                "type": "string",
                "description": f"The {param.replace('_', ' ')}",
                "example": f"example-{param}"
            }
        } for param in path_params]
    
    # Add request body if available
    if request_schema and request_example is not None:
        operation["requestBody"] = {
            "description": "Request payload",
            "required": True,
            "content": {
                request_content_type: {
                    "schema": request_schema,
                    "example": request_example
                }
            }
        }
    
    # Add endpoint-specific security if not global
    if 'security' not in spec and 'components' in spec and 'securitySchemes' in spec['components']:
        if input(f"Add authentication to this endpoint? (y/n) [y]: ").lower() != 'n':
            auth_type = next(iter(spec['components']['securitySchemes'].values()))['type']
            operation["security"] = [{f"{auth_type}Auth": []}]
    
    spec["paths"][path] = {method: operation}
    
    # Save the spec
    filename = input("\nOutput filename [openapi.yaml]: ").strip() or "openapi.yaml"
    with open(filename, 'w') as f:
        yaml.dump(spec, f, sort_keys=False)
    
    print(f"\nOpenAPI specification saved to {filename}")

if __name__ == "__main__":
    build_openapi_spec()