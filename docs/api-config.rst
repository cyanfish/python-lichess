API Client Configuration
==========================================

The :class:`~lichess.api.DefaultApiClient` is used to perform the actual HTTP requests. It also manages rate-limiting and retries.

If you need more functionality, you can subclass it. To use a custom client, set :class:`~lichess.api.default_client` or use the :data:`client` parameter in each API method wrapper.
   
.. automodule:: lichess.api
    :members: ApiError, ApiHttpError, DefaultApiClient, default_client
