To add a backend, add a python file to `src/backends/`.
There is no restriction on the module name.
The module must contain the following functions:

- `get_registered_extensions`: returns a list containing extensions that the parser knows how to read
- `load`: given an open file, returns a dict representing the parsed contents of the file (technically, it can return any instance of `collections.abc.Mapping`)

See `src/backends/json.py` for a simple example or `src/backends/ini.py` for a
more complicated one that requires wrapping a different API.

Feel free to make a pull request with a new backend.
If it's not for a common format, please add at least one example configuration file.
