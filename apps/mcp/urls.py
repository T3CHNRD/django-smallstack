"""URL config for apps/mcp. Filled in by phase 13."""

from django.urls import path

app_name = "mcp"

urlpatterns: list[path] = []

# Exported separately so config/urls.py can mount these at the root for the
# RFC 8414 / RFC 9728 well-known discovery paths.
oauth_wellknown_urlpatterns: list[path] = []
