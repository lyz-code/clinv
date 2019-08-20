# Hacking

This program is developed with
[TDD](https://en.wikipedia.org/wiki/Test-driven_development), so if you want to
add code, you would most likely should add tests. If you don't know how, say so
in the pull request and we'll try to help you.

All classes, methods and modules are meant to have docstrings, so please add
them.

## Create a new source

For the purpose of this section, we'll assume that the new source we want to add
to our inventory is called `newsource`.

### Fetch the information

On `clinv/clinv.py` add the `fetch_newsource_inventory` method to fetch the
information from your source
