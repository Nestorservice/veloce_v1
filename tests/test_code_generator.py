import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from veloce.code_generator import CodeGenerator


@pytest.fixture
def mock_ai():
    client = MagicMock()
    client.complete = AsyncMock(return_value='package main\n\nfunc Hello() string { return "world" }')
    return client


@pytest.mark.asyncio
async def test_generates_go_file_from_php_batch(mock_ai, tmp_path):
    php_file = tmp_path / "UserService.php"
    php_file.write_text("<?php class UserService {}")
    backend = tmp_path / "backend"
    backend.mkdir()

    gen = CodeGenerator(mock_ai, go_output=str(backend), flutter_output=str(tmp_path / "frontend"), sleep_seconds=0)
    result = await gen.translate_batch([php_file], batch_index=1)

    assert len(result.go_files) == 1
    assert Path(result.go_files[0]).exists()


@pytest.mark.asyncio
async def test_generates_dart_file_from_blade_batch(mock_ai, tmp_path):
    blade_file = tmp_path / "home.blade.php"
    blade_file.write_text("{{ $user }}")
    frontend = tmp_path / "frontend"
    frontend.mkdir()

    gen = CodeGenerator(mock_ai, go_output=str(tmp_path / "backend"), flutter_output=str(frontend), sleep_seconds=0)
    result = await gen.translate_batch([blade_file], batch_index=1)

    assert len(result.dart_files) == 1
    assert Path(result.dart_files[0]).exists()


@pytest.mark.asyncio
async def test_empty_batch_returns_empty_result(mock_ai, tmp_path):
    gen = CodeGenerator(mock_ai, go_output=str(tmp_path), flutter_output=str(tmp_path), sleep_seconds=0)
    result = await gen.translate_batch([], batch_index=1)
    assert result.go_files == []
    assert result.dart_files == []
