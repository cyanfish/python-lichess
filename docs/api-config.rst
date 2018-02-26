API Client Configuration
==========================================

The :class:`~lichess.api.DefaultApiClient` is used to perform the actual HTTP requests. It can be customized by setting :class:`~lichess.api.base_url` or :class:`~lichess.api.on_rate_limit`.
Alternatively, you can create your own API client if you need more customizability (e.g. to coordinate API use over multiple threads). To use a custom client, set :class:`~lichess.api.default_client` or use the :data:`client` parameter in the API method wrapper.
   
.. automodule:: lichess.api
    :members: ApiError, ApiHttpError, DefaultApiClient, default_client, base_url, on_rate_limit
