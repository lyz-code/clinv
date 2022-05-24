Date: 2022-05-23

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->
We start to have enough information in the inventory to give a rough idea of the
security measures and risks of the different services, and it would be
interesting to have an ordered list of services by some risk level that takes
into account this data.

The model can always be refined further to better reflect the reality, for
example, if a service has different access methods one for admins and other for
common users, but we'll start with what we have.

# Proposals
<!-- What are the possible solutions to the problem described in the context -->

## Score types

Build three scores per service:

* `risk`: Measures the danger level of the service, taking into account the
    value of the information or detected service hazards.
* `protection`: Measures the level of protection of the service.
* `security`: Takes into account the above scores to output an overall one.

### Risk

For the `risk` we may start with:

* The number of `Information` entities accessed by the service.
* A list of common risks.

In the next iteration, we could give the `Information` model a `risk` attribute
to refine even further that element.

The list of common risks could be a `str` `Enum` similar to the `NetworkAccess`
or the `AuthenticationMethod`.

### Protection

For the `protection` score we may start with:

* A base score given by the `NetworkAccess` that's big enough to separate the
    services despite the number of security  measures that they've got
    implemented.
* A list of common security measures, it could be a `str` `Enum` similar to the
    `NetworkAccess` or the `AuthenticationMethod`.

### Security

A simple subtraction of `protection` - `risk` may suffice.

## How to give values

So far we have based the possible cases of the elements in `str Enums`, we could
use `IntEnums` but then we'd need to deduce the element name from
a transformation from the `Enum` key, which won't be always the best. For
example it would be difficult going from `TWOFA_KEY` to a user pleasant string.

Another option would be to create `Entity` for each element with something
like:

```python
class Risk(Entity):
    id_: RiskID
    name: str
    value: int
```

But then we'll need to:

* Populate the initial values of the database
* Change the schema of the services
* Tweak the `services.build_choices` to include the schema changes, although it
    looks easy.

On the other side:

* It will be easier for downstream users to define their own network accesses,
    authenticated methods, security measures...
* It will be easier to expand the model for example with different access
    methods for each service.

## How to add new risk or security measure

We can reuse most of the `add` cli method, but it would be kind of cool if at
the end of the form, it supported the addition of the element to the existing
services.

## How to deal with the change of schema

We'll give a script to create the base elements and show a warning in the commit
of the database schema and what steps needs to be done.

# Decision
<!-- What is the change that we're proposing and/or doing? -->

* Create two new models `Risk` and `SecurityMeasure`.
* Tweak the `add` entrypoint to accept these two new models.
* Create a new entrypoint to return an ordered list of services based on the
  stored information.
* Create a script to do the initial population of the database.

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
