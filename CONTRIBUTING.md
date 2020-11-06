# CONTRIBUTING  

We tried to split development dependencies from the main installation one to ensure the deployments do not install 
redundant software.

For that reason, you can simply install the `requirements_dev.txt` which adds some dependencies for development purposes, 
like `pytest`, or `pre-commit`.

1. Create a new `virtualenv`: `python -m venv env`
2. Source it: `source env/bin/activate`
3. Install the requirements: `pip install -r requirements_dev.txt`
4. If you are going to do some development, please install the `pre-commit` hooks with `pre-commit install`.
5. You're ready to go.

_Note_: Keep in mind that you will need a tunnel like [ngrok](https://ngrok.com) to test your local changes with the 
live API integration.


## Submitting a PR  
Feel free to fork the project, do the work you need, and submit a PR back to us. We have a CI/CD workflow in place. 
We cannot accept PRs with failing pipelines, thus we recommend you install our git hooks.
That itself avoids errors related with formatting, insecure code, and other similar things.

All contributions are welcome but they all should go along with the corresponding unit, or integration test. 

We take pride in ensuring code quality, and there is no better way to do that than with automated tests. Not only we are 
ensuring that core functionalities of the project work throughout time, we are also facilitating all contributions, 
making us confident that it is okay to on-board new code.

## Code structure  
Getting started with an unknown project is sometimes intimidating. In hopes to help flatten the learning curve, here 
are some notes on how the code is organized:

- The `main.py` file contains the logic required to start a Flask app. It makes use of `python-dotenv` to load the 
  `.env` and `.flaskenv` into memory - and uses these environments variables in the code.
- `server.py` is the file in which the server is fully specified. Any new middleware or endpoint, should go in there.
- `signatures.py` takes care of parsing the config to python objects.
- `blacklists.py` same as signatures but for blacklists.
- `gitlcient` package contains the base implementation in the init, and all client's (GitLab, GitHub soon, Bitbucket, 
  ...), should be implemented here. 
- `data` package contains all data-only objects.
