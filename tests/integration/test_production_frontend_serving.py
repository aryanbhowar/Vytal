"""Production mode: the backend serves the built website and the API on one port.

Uses a tiny SYNTHETIC build folder so the test does not depend on `npm run build`.
"""

import pytest


@pytest.fixture
def production_client(make_client, tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>Vytal test build</title>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log('test')", encoding="utf-8")
    (dist / "favicon.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("outside the build folder", encoding="utf-8")
    return make_client(serve_frontend=True, frontend_dist_dir=dist, enable_api_docs=False)


def test_root_and_client_routes_return_the_app(production_client):
    for path in ("/", "/assessment", "/results", "/methodology"):
        response = production_client.get(path)
        assert response.status_code == 200
        assert "Vytal test build" in response.text
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_static_files_are_served(production_client):
    assert production_client.get("/assets/app.js").text == "console.log('test')"
    assert production_client.get("/favicon.svg").status_code == 200


def test_api_still_works_and_unknown_api_paths_are_404(production_client):
    assert production_client.get("/api/health").json()["status"] == "ok"
    response = production_client.get("/api/nope")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_files_outside_the_build_folder_are_not_served(production_client):
    for path in ("/../secret.txt", "/%2e%2e/secret.txt", "/assets/../../secret.txt"):
        assert "outside the build folder" not in production_client.get(path).text


def test_api_docs_are_off_in_production(production_client):
    docs = production_client.get("/docs")
    assert "swagger" not in docs.text.lower()  # falls through to the app shell instead
    assert '"openapi"' not in production_client.get("/openapi.json").text


def test_frontend_not_served_unless_enabled(client):
    assert client.get("/").status_code == 404
