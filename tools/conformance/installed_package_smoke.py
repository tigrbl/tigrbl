from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import textwrap
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / 'pkgs' / 'core' / 'tigrbl'
NATIVE_PY_PATH = ROOT / 'pkgs' / 'core' / 'tigrbl_runtime'
CORE_INSTALL_DIRS = [
    ROOT / 'pkgs' / 'core' / 'tigrbl_typing',
    ROOT / 'pkgs' / 'core' / 'tigrbl_spec',
    ROOT / 'pkgs' / 'core' / 'tigrbl_base',
    ROOT / 'pkgs' / 'core' / 'tigrbl_core',
    ROOT / 'pkgs' / 'core' / 'tigrbl_canon',
    ROOT / 'pkgs' / 'core' / 'tigrbl_runtime',
    ROOT / 'pkgs' / 'core' / 'tigrbl_atoms',
    ROOT / 'pkgs' / 'core' / 'tigrbl_kernel',
    ROOT / 'pkgs' / 'core' / 'tigrbl_ops_oltp',
    ROOT / 'pkgs' / 'core' / 'tigrbl_orm',
    ROOT / 'pkgs' / 'core' / 'tigrbl_concrete',
]
TARGET_DEPS = [
    'sqlalchemy>=2.0',
    'aiosqlite>=0.19.0',
]


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd or ROOT, env=env, check=True, capture_output=True, text=True)


def build_artifacts(out_dir: Path) -> tuple[Path, Path]:
    run([sys.executable, '-m', 'build', str(PACKAGE_DIR), '--wheel', '--sdist', '--outdir', str(out_dir)])
    wheels = sorted(out_dir.glob('*.whl'))
    sdists = sorted(out_dir.glob('*.tar.gz'))
    if not wheels or not sdists:
        raise SystemExit('expected both wheel and sdist artifacts')
    return wheels[0], sdists[0]


def wheel_entry_points(wheel_path: Path) -> dict[str, str]:
    with ZipFile(wheel_path) as zf:
        entry_name = next(name for name in zf.namelist() if name.endswith('entry_points.txt'))
        text = zf.read(entry_name).decode('utf-8')
    result: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('[') and line.endswith(']'):
            current = line[1:-1]
            continue
        if current == 'console_scripts' and '=' in line:
            name, value = [part.strip() for part in line.split('=', 1)]
            result[name] = value
    return result


def inspect_sdist(sdist_path: Path) -> dict[str, bool]:
    with tarfile.open(sdist_path, 'r:gz') as tf:
        names = tf.getnames()
    return {
        'contains_pyproject': any(name.endswith('/pyproject.toml') for name in names),
        'contains_readme': any(name.endswith('/README.md') for name in names),
        'contains_cli': any(name.endswith('/tigrbl/cli.py') for name in names),
    }


def create_app_fixture(dirpath: Path) -> Path:
    fixture = dirpath / 'phase12_installed_app.py'
    fixture.write_text(
        textwrap.dedent(
            '''
            from __future__ import annotations
            from tigrbl import TigrblApp, TigrblRouter

            app = TigrblApp(title="Phase 12 Installed App", version="12.0.0", mount_system=False)
            router = TigrblRouter()

            @router.get("/ping")
            def ping() -> dict[str, bool]:
                return {"ok": True}

            @router.websocket("/ws/echo")
            async def echo_socket(ws) -> None:
                await ws.accept()
                await ws.close()

            app.include_router(router)
            '''
        ).strip() + '\n',
        encoding='utf-8',
    )
    return fixture


def make_env(site_dir: Path) -> dict[str, str]:
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join([str(site_dir), str(NATIVE_PY_PATH)])
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def cli_json(site_dir: Path, target: str, *args: str) -> dict:
    cp = run([sys.executable, '-m', 'tigrbl', *args, target], env=make_env(site_dir))
    return json.loads(cp.stdout)


def cli_text(site_dir: Path, target: str, *args: str) -> str:
    cp = run([sys.executable, '-m', 'tigrbl', *args, target], env=make_env(site_dir))
    return cp.stdout


def run_server_translation_smoke(site_dir: Path) -> dict[str, dict[str, object]]:
    script = textwrap.dedent(
        '''
        import json
        import sys
        import types
        from tigrbl import cli as tigrbl_cli

        results = {}
        cap = {}
        sys.modules['uvicorn'] = types.SimpleNamespace(run=lambda app, **kwargs: cap.update(kwargs))
        cfg = tigrbl_cli.ServeConfig(server='uvicorn', host='0.0.0.0', port=9001, workers=2, root_path='/root', proxy_headers=True)
        tigrbl_cli._run_with_uvicorn(object(), cfg)
        results['uvicorn'] = {'host': cap['host'], 'port': cap['port'], 'root_path': cap['root_path'], 'proxy_headers': cap['proxy_headers']}

        cap = {}
        fake_asyncio_mod = types.ModuleType('hypercorn.asyncio')
        fake_asyncio_mod.serve = lambda app, config: (cap.update({'bind': list(config.bind), 'workers': config.workers, 'root_path': config.root_path, 'proxy_mode': config.proxy_mode}) or 'fake-coro')
        fake_config_mod = types.ModuleType('hypercorn.config')
        class FakeConfig:
            def __init__(self):
                self.bind = []
                self.use_reloader = False
                self.workers = 1
                self.root_path = ''
                self.proxy_mode = None
        fake_config_mod.Config = FakeConfig
        sys.modules['hypercorn.asyncio'] = fake_asyncio_mod
        sys.modules['hypercorn.config'] = fake_config_mod
        orig_run = tigrbl_cli.asyncio.run
        tigrbl_cli.asyncio.run = lambda _coro: None
        try:
            cfg = tigrbl_cli.ServeConfig(server='hypercorn', host='0.0.0.0', port=9001, workers=2, root_path='/root', proxy_headers=True)
            tigrbl_cli._run_with_hypercorn(object(), cfg)
        finally:
            tigrbl_cli.asyncio.run = orig_run
        results['hypercorn'] = cap

        orig = tigrbl_cli._GunicornApplication.run
        cap = {}
        def fake_run(self):
            cap.update(self.options)
        tigrbl_cli._GunicornApplication.run = fake_run
        try:
            cfg = tigrbl_cli.ServeConfig(server='gunicorn', host='0.0.0.0', port=9001, workers=2, root_path='/root', proxy_headers=True)
            tigrbl_cli._run_with_gunicorn(object(), cfg)
        finally:
            tigrbl_cli._GunicornApplication.run = orig
        results['gunicorn'] = {'bind': cap['bind'], 'workers': cap['workers'], 'worker_class': cap['worker_class'], 'forwarded_allow_ips': cap['forwarded_allow_ips']}

        cap = {}
        sys.modules['tigrcorn'] = types.SimpleNamespace(run=lambda app, **kwargs: cap.update(kwargs))
        cfg = tigrbl_cli.ServeConfig(server='tigrcorn', host='0.0.0.0', port=9001, workers=2, root_path='/root', proxy_headers=True)
        tigrbl_cli._run_with_tigrcorn(object(), cfg)
        results['tigrcorn'] = {'host': cap['host'], 'port': cap['port'], 'workers': cap['workers'], 'root_path': cap['root_path'], 'proxy_headers': cap['proxy_headers']}

        print(json.dumps(results, sort_keys=True))
        '''
    )
    cp = run([sys.executable, '-c', script], env=make_env(site_dir))
    return json.loads(cp.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-out')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        dist = tmp / 'dist'
        site = tmp / 'site'
        dist.mkdir()
        site.mkdir()
        wheel, sdist = build_artifacts(dist)
        wheel_eps = wheel_entry_points(wheel)
        sdist_info = inspect_sdist(sdist)

        run([sys.executable, '-m', 'pip', 'install', '--target', str(site), *TARGET_DEPS])
        for pkg in CORE_INSTALL_DIRS:
            run([
                sys.executable,
                '-m',
                'pip',
                'install',
                '--ignore-requires-python',
                '--no-deps',
                '--no-build-isolation',
                '--target',
                str(site),
                str(pkg),
            ])
        run([
            sys.executable,
            '-m',
            'pip',
            'install',
            '--ignore-requires-python',
            '--no-deps',
            '--target',
            str(site),
            str(wheel),
        ])

        fixture = create_app_fixture(tmp)
        target = f'{fixture}:app'
        capabilities = cli_json(site, target, 'capabilities')
        openapi = cli_json(site, target, 'openapi')
        openrpc = cli_json(site, target, 'openrpc')
        doctor = cli_json(site, target, 'doctor')
        routes = cli_text(site, target, 'routes')
        server_translation = run_server_translation_smoke(site)

        manifest = {
            'package_dir': str(PACKAGE_DIR.relative_to(ROOT)),
            'wheel': wheel.name,
            'sdist': sdist.name,
            'wheel_entry_points': wheel_eps,
            'sdist_contents': sdist_info,
            'install_mode': 'isolated target install root',
            'rust_binding_support': 'source-path fallback via pkgs/core/tigrbl_runtime',
            'installed_cli': {
                'commands': capabilities['commands'],
                'flags': capabilities['flags'],
                'servers': capabilities['servers'],
                'app_title': capabilities['app']['title'],
            },
            'openapi_version': openapi['openapi'],
            'openrpc_version': openrpc['openrpc'],
            'doctor_title': doctor['title'],
            'doctor_version': doctor['version'],
            'routes_contains': {
                '/ping': '/ping' in routes,
                '/ws/echo': '/ws/echo' in routes,
                '/docs': '/docs' in routes,
                '/openapi.json': '/openapi.json' in routes,
                '/openrpc.json': '/openrpc.json' in routes,
                '/lens': '/lens' in routes,
            },
            'server_translation': server_translation,
        }
        if args.manifest_out:
            out = Path(args.manifest_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
