# OpenAPI Specification Generator

A Python script that automatically generates valid OpenAPI 3.0 specifications (YAML format) from example files, with support for authentication and comprehensive documentation.

## Features

- Generates validation-proof OpenAPI 3.0 specs
- Supports JSON, HTML, text, and XML examples
- Automatic type detection and documentation
- Built-in authentication configuration
- Simple one-endpoint-per-run workflow

## Installation

1. Ensure Python 3.6+ is installed
2. Install dependencies:
   ```bash
   pip install pyyaml
   ```

## Usage

### Basic Execution

1. Prepare your example files:
   - `request.json` (for POST/PUT/PATCH)
   - `response.json` (required)

2. Run the script:
   ```bash
   python openapi_builder.py
   ```

### Interactive Prompts

| Prompt | Description | Options/Examples |
|--------|-------------|------------------|
| API Title | Your API's name | `Pet Store API` |
| API Version | Version number | `1.0.0` |
| API Description | Brief description | `Manage pets and orders` |
| Base URL | Your API's base URL | `https://api.example.com` |
| Authentication Type | Security scheme | `1. API Key`, `2. HTTP Basic`, `3. OAuth 2.0`, `4. OpenID Connect`, `none` |
| Endpoint path | The API endpoint path | `/pets/{id}` |
| HTTP Method | The HTTP method | `get`, `post`, `put`, `delete`, `patch` |
| Request example file | Path to request example | `request.json` |
| Response example file | Path to response example | `response.json` |
| Output filename | Generated spec filename | `openapi.yaml` |

### Authentication Options

Depending on your chosen auth type, you'll see additional prompts:

**API Key:**
- Parameter name (default: `api_key`)
- Location (`header`, `query`, or `cookie`)
- Description

**HTTP Basic/Bearer:**
- Scheme (`basic` or `bearer`)
- Bearer format (e.g., `JWT`)

**OAuth2/OpenID:**
- Authorization URL
- Token URL
- Scopes (format: `scope:description`)

## Example Workflow

1. Create example files:
   - `request.json`:
     ```json
     {"name": "Fluffy", "type": "cat", "age": 3}
     ```
   - `response.json`:
     ```json
     {"id": 123, "name": "Fluffy", "status": "created"}
     ```

2. Run the script:
   ```bash
   $ python openapi_builder.py
   API Title: Pet Store API
   API Version [1.0.0]: 
   API Description (optional): Manage pets
   Base URL [https://api.example.com]: https://api.petstore.com/v1
   
   === Authentication Setup ===
   Select authentication type:
   1. API Key
   2. HTTP Basic
   3. OAuth 2.0
   4. OpenID Connect
   none. No authentication
   Your choice [none]: 1
   Header/query parameter name [api_key]: petstore_key
   Location (header/query/cookie) [header]: 
   Description [API key authentication]: 
   
   Apply this security globally to all endpoints? (y/n) [y]: 
   
   Endpoint path (e.g. '/pets/{id}'): /pets/{id}
   HTTP Method [put]: 
   Request example file (e.g. request.json): request.json
   Response example file (e.g. response.json): response.json
   
   Output filename [openapi.yaml]: petstore.yaml
   ```

3. Generated file will be saved as `petstore.yaml`

## Manual Editing Tips

After generation, you may want to manually edit the YAML file:

1. **Common Edits**:
   - Add more endpoints (duplicate and modify existing path entries)
   - Edit descriptions
   - Add/enum values
   - Mark fields as required

2. **Example Edits**:

   ```yaml
   paths:
     /pets/{id}:
       put:
         description: "Update an existing pet"  # ← Edit description
         requestBody:
           content:
             application/json:
               schema:
                 required: ["name"]  # ← Add required fields
                 properties:
                   age:
                     minimum: 0  # ← Add validation
                     maximum: 30
   ```

3. **Validation**:
   - Always validate your edited YAML using:
     - [Swagger Editor](https://editor.swagger.io/)
     - `swagger-cli validate petstore.yaml`

## Best Practices

1. **For JSON APIs**:
   - Provide comprehensive example files
   - Include all possible fields
   - Use descriptive field names

2. **For Non-JSON APIs**:
   - The generator will create simpler documentation
   - Add manual descriptions as needed

3. **Authentication**:
   - For complex OAuth flows, you may need to manually edit scopes
   - Add security requirements per-endpoint if needed

## Limitations

- Designed for single endpoint documentation
- Complex array schemas may need manual editing
- For multi-endpoint APIs, run multiple times and merge files
