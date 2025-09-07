# Maintaining LinkedIn API Access

The LinkedIn job scraping functionality in this application relies on using a valid, authenticated session from a web browser. This is because LinkedIn's internal GraphQL API is not public and requires active cookies and a CSRF token to work.

These credentials expire, usually after a few hours or days. When they do, the application will fail with a `400 Bad Request` error.

## How to Update Your Credentials

Follow these steps to get fresh credentials and update the application.

1.  **Open LinkedIn in Your Browser**: Log in to your LinkedIn account.

2.  **Navigate to the Jobs Page**: Go to [linkedin.com/jobs](https://www.linkedin.com/jobs).

3.  **Open Developer Tools**: Press `F12` (or `Cmd+Option+I` on Mac) to open the browser's developer tools.

4.  **Go to the Network Tab**: Click on the "Network" tab in the developer tools.

5.  **Perform a Job Search**: Type a keyword (e.g., "Python") into the search bar and press Enter. You will see a list of network requests appear in the Network tab.

6.  **Find the GraphQL Request**:
    *   In the filter bar of the Network tab, type `graphql` to find the relevant API call.
    *   Look for a request that starts with `graphql?variables=(...`. Click on it.

7.  **Copy the cURL Command**:
    *   With the request selected, right-click on it.
    *   Go to **Copy** > **Copy as cURL**.

8.  **Extract the `Cookie` and `csrf-token`**:
    *   Paste the copied cURL command into a text editor.
    *   Find the line that starts with `-H 'cookie: ...'`. Copy the entire value inside the single quotes. This is your `LINKEDIN_COOKIE`.
    *   Find the line that starts with `-H 'csrf-token: ...'`. Copy the value inside the single quotes. This is your `CSRF_TOKEN`.

9.  **Update the `.env` File**:
    *   Open the `.env` file in the root of this project.
    *   Replace the existing values for `LINKEDIN_COOKIE` and `CSRF_TOKEN` with the new ones you just copied.

    ```dotenv
    # .env file
    LINKEDIN_COOKIE="<paste your new cookie string here>"
    CSRF_TOKEN="<paste your new csrf-token here>"
    ```

10. **Restart the Application**: If your server is running, restart it to ensure it loads the new environment variables.

Your application should now be able to successfully fetch data from LinkedIn again.
