Date: 2022-05-24

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
The CLI starts having bad performance, specially:

* `clinv add ser`: Due to the `service.build_choices`.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## `service.build_choices`

We could:

* Migrate to another database backend to speed up the queries.
* Build the choices on the go instead of at initialization
* Save the choices in a key-value storage either redis or a local cache

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
