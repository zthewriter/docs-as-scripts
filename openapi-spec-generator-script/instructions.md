# OpenAPI Schema Generator

A Python script that automatically generates OpenAPI 3.0 specifications (YAML format) from simple endpoint definitions. This tool simplifies API documentation by converting basic endpoint information into fully compliant OpenAPI schemas.

## Features

- Generates OpenAPI 3.0 YAML specifications
- Supports all major HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Automatically detects request/response content types
- Handles JSON, plain text, HTML, and image responses
- Supports path parameters and collection-based endpoints
- Includes standard error responses (400, 401, 403, 500)
- Built-in security scheme for bearer token authentication

## Why Use This Script?

- **Save time**: Automate your API documentation process instead of writing OpenAPI specs manually
- **Reduce errors**: Ensure your documentation follows the OpenAPI specification correctly
- **Consistency**: Maintain a standard structure across all your API endpoints
- **Flexibility**: Easily modify the template to match your API's specific needs
- **Integration**: Generate specs that work with Swagger UI, Redoc, and other API documentation tools

## How It Works

The script takes basic information about your API endpoint and:
1. Analyzes your request/response examples to determine data types
2. Generates appropriate schema definitions
3. Structures the path, parameters, request body, and responses
4. Outputs a complete OpenAPI 3.0 specification in YAML format

## Installation

1. Ensure you have Python 3.6+ installed
2. Clone this repository or download the script
3. Install the required dependencies:

```bash
pip install pyyaml
```

## Usage

### Basic Usage

1. Edit the `main()` function in the script to set your endpoint details:

```python
# Input fields with default values
endpoint_title = "Get User Info"
endpoint_description = "Retrieves user information."
endpoint_path = "users/{userId}"
http_method = "GET"
response_content_type = ""
is_part_of_collection = "No"
request_example_json = ""
response_example_json = ""
```

2. Run the script:

```bash
python openapi_generator.py
```

3. The generated OpenAPI schema will be:
   - Printed to the console
   - Saved to `openapi_schema.yaml`

### Advanced Usage

For more control, you can:
- Directly call `generate_openapi_schema()` with your parameters
- Modify the template in the script to match your API's base URL and security requirements
- Chain multiple endpoint generations to create a complete API specification

### Input Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `endpoint_title` | Short title for your endpoint | "Create New User" |
| `endpoint_description` | Detailed description of the endpoint | "Creates a new user account with the provided information" |
| `endpoint_path` | API path with parameters in curly braces | "users/{userId}" |
| `http_method` | HTTP method for the endpoint | "POST" |
| `request_example` | Example request body (dict for JSON, string for text) | `{"name": "John", "email": "john@example.com"}` |
| `response_example` | Example response body | `{"id": 123, "status": "created"}` |
| `response_content_type` | Force specific response content type | "application/json" |
| `is_part_of_collection` | Whether endpoint belongs to a collection ("Yes"/"No") | "Yes" |

## Example Output

```yaml
openapi: 3.0.0
info:
  title: Get User Info
  description: Retrieves user information.
  version: 1.0.0
servers:
  - url: https://api.example.com
    description: Base URL for the API
paths:
  /v1/users/{userId}:
    get:
      summary: Get User Info
      description: Retrieves user information.
      security:
        - bearerAuth: []
      responses:
        200:
          description: Successful response
          content:
            application/json:
              schema:
                type: object
              example:
                id: 123
                name: John Doe
                email: john@example.com
        400:
          description: Bad request
        401:
          description: Unauthorized
        403:
          description: Forbidden
        500:
          description: Internal Server Error
```

## Customization

To adapt the script to your specific needs:

1. **Change the base URL**: Edit the `servers` section in the template
2. **Modify security schemes**: Update the `components.securitySchemes` section
3. **Add standard responses**: Include more response codes in the template
4. **Extend type support**: Enhance the `json_to_schema_properties()` function for more data types

## Limitations

- Currently focuses on single endpoint generation
- Basic type inference (can be extended as needed)
- Simple authentication scheme (bearer token)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## License

MIT License - free to use and modify
```

This README provides:
1. A clear overview of the project
2. Installation instructions
3. Usage examples
4. Explanation of how it works
5. Customization options
6. Example output
7. Project limitations