# Operator, documentation, and HTTP surface evidence

Run date: 2026-04-27

Commands:

- `.venv\Scripts\python.exe -m pytest pkgs\core\tigrbl_tests\tests\unit\test_http_route_registration.py pkgs\core\tigrbl_tests\tests\unit\test_system_docs_builders.py pkgs\core\tigrbl_tests\tests\unit\decorators\test_declarative_surface.py -q`
- `.venv\Scripts\python.exe -m pytest pkgs\core\tigrbl_tests\tests\unit\test_operator_surface_closure.py pkgs\core\tigrbl_tests\tests\unit\test_operator_surface_docs_parity.py pkgs\core\tigrbl_tests\tests\unit\test_declared_surface_docs.py -q --basetemp .\.tmp\pytest-operator-surface`

Results:

- HTTP route registration, system docs builders, and declarative decorator surface: 19 passed.
- Operator surface closure, operator docs parity, and declared-surface docs: 10 passed.

Certification decision:

The canonical HTTP route registration, documentation support, declared-surface docs extension, and operator streaming, WebSocket, SSE, form, multipart, and uploaded-file surfaces have current focused passing evidence. These rows may be treated as implemented for the active registry as long as their linked claims remain attached to the passing evidence above and prior passed closure evidence.
