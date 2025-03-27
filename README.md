## Running the Workflow
1. Create a .env file with an OpenAI API key in it
2. run the command `cd webapp && python -m http.server 8080`
3. Run the command `poetry run python pyapp/app.py` in a second terminal
4. The app should now be accessible at `http://localhost:8080/index.html`
    a. Note the App will take a minute to load while pyodide pulls the required packages

## TODO:

- [ ] Have the ability to locally cache pyodide and dependencies