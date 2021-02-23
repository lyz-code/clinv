Date: 2021-03-31

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Accepted

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->

The codebase of the project has grown old pretty fast, there are the next
problems:

* The code structure doesn't comply with the domain driven design structure I'm
using with the rest of my projects, that means that maintaining it is
uncomfortable for me. I can't use the cookiecutter template to adapt the
improvements I do on other projects.
* There is a high coupling between an adapter (aws) and the storage solution.
* I'm using argparse instead of click to define the cli
* A lot of the testing is done using mocks, instead of having a pyramid of unit
    and e2e tests.
* The model and service functionality is all mixed up in the models.
* The performance is bad when you have many resources.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->
* Refactor the code to use the domain driven design structure.
* Make it compliant with the [cookiecutter python
    template](https://github.com/lyz-code/cookiecutter-python-project).
* Migrate cli definition to click.
* Add type hints

# Decision
<!-- What is the change that we're proposing and/or doing? -->
Implement the only proposal

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
