import pytest
from pathlib import Path
from veloce.php_scanner import PHPScanner


@pytest.fixture
def fake_laravel(tmp_path):
    # Fichiers metier a inclure
    (tmp_path / "app" / "Models").mkdir(parents=True)
    (tmp_path / "app" / "Models" / "User.php").write_text("<?php class User {}")
    (tmp_path / "resources" / "views").mkdir(parents=True)
    (tmp_path / "resources" / "views" / "home.blade.php").write_text("{{ $user }}")
    (tmp_path / "app" / "Http" / "Controllers").mkdir(parents=True)
    (tmp_path / "app" / "Http" / "Controllers" / "AuthController.php").write_text("<?php class Auth {}")

    # Fichiers a exclure
    (tmp_path / "vendor" / "laravel").mkdir(parents=True)
    (tmp_path / "vendor" / "laravel" / "framework.php").write_text("<?php // vendor")
    (tmp_path / "storage" / "logs").mkdir(parents=True)
    (tmp_path / "storage" / "logs" / "laravel.log").write_text("log")
    (tmp_path / "bootstrap" / "cache").mkdir(parents=True)
    (tmp_path / "bootstrap" / "cache" / "config.php").write_text("<?php // cache")
    return tmp_path


def test_finds_php_and_blade_files(fake_laravel):
    files = PHPScanner(str(fake_laravel)).scan()
    names = [f.name for f in files]
    assert "User.php" in names
    assert "home.blade.php" in names
    assert "AuthController.php" in names


def test_excludes_vendor_cache_logs(fake_laravel):
    files = PHPScanner(str(fake_laravel)).scan()
    # Utiliser les chemins relatifs pour eviter les faux positifs
    # (le nom du test contient "vendor", qui apparait dans le tmp_path absolu)
    rel_paths = [str(f.relative_to(fake_laravel)) for f in files]
    assert not any("vendor" in p for p in rel_paths)
    assert not any("cache" in p for p in rel_paths)
    assert not any(".log" in p for p in rel_paths)


def test_returns_exactly_three_business_files(fake_laravel):
    files = PHPScanner(str(fake_laravel)).scan()
    assert len(files) == 3


def test_returns_path_objects(fake_laravel):
    files = PHPScanner(str(fake_laravel)).scan()
    assert all(isinstance(f, Path) for f in files)
