Assignment Explanations

Task 3: API Endpoints and Behavior
Calling /predict without the location parameter:

Behavior: The request succeeds and returns a valid price prediction.

Reason: The location query parameter is defined with a default value ("other"). When omitted in the HTTP request, FastAPI automatically assigns this default value.

Calling /predict without the area parameter:

Behavior: Returns an HTTP 422 Unprocessable Entity error.

Reason: area is a required query parameter without any default value. Missing a required parameter violates FastAPI's request validation rules.

Task 5: Static Files and Relative URLs
Why a relative URL (/predict) works seamlessly:

Since the static HTML page (/static/house_form.html) and the API endpoint (/predict) are hosted on the same origin (same protocol, domain, and port: http://127.0.0.1:8000), relative fetch URLs resolve directly relative to the server origin. This setup completely avoids Cross-Origin Resource Sharing (CORS) restrictions.

Task 6 (Bonus): Query Parameters vs JSON Body
GET Request with Query Parameters (GET /predict):

Data is passed directly in the URL query string (e.g., /predict?area=80&bedrooms=3).

Best suited for simple data retrieval; parameters are visible in browser history and server logs.

POST Request with JSON Body (POST /predict):

Data is sent inside the HTTP request payload formatted as a JSON object.

Better suited for complex, nested data structures or sensitive payloads as it keeps data out of the URL bar.
