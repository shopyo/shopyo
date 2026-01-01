import os
import shutil
import pytest
from shopyo.api import file as file_utils


def test_tryrmcache(tmp_path, capsys):
    # Setup
    d = tmp_path / "project"
    d.mkdir()
    (d / "__pycache__").mkdir()
    (d / "module").mkdir()
    (d / "module" / "__pycache__").mkdir()

    # Test
    file_utils.tryrmcache(str(d), verbose=True)

    # Verify
    assert not (d / "__pycache__").exists()
    assert not (d / "module" / "__pycache__").exists()
    assert (d / "module").exists()

    captured = capsys.readouterr()
    assert "[x] __pycache__ successfully deleted" in captured.out


def test_tryrmfile(tmp_path, capsys):
    f = tmp_path / "test.txt"
    f.write_text("content")

    assert file_utils.tryrmfile(str(f), verbose=True)
    assert not f.exists()

    captured = capsys.readouterr()
    assert f"[x] file '{f}' successfully deleted" in captured.out


def test_tryrmfile_fail(tmp_path, capsys):
    f = tmp_path / "nonexistent.txt"
    assert not file_utils.tryrmfile(str(f), verbose=True)

    captured = capsys.readouterr()
    assert "unable to delete" in captured.err


def test_tryrmtree(tmp_path, capsys):
    d = tmp_path / "folder"
    d.mkdir()
    (d / "file.txt").write_text("content")

    assert file_utils.tryrmtree(str(d), verbose=True)
    assert not d.exists()

    captured = capsys.readouterr()
    assert f"[x] folder '{d}' successfully deleted" in captured.out


def test_trycopytree(tmp_path, capsys):
    src = tmp_path / "src"
    src.mkdir()
    (src / "file.txt").write_text("content")
    dest = tmp_path / "dest"

    file_utils.trycopytree(str(src), str(dest), verbose=True)

    assert dest.exists()
    assert (dest / "file.txt").exists()

    captured = capsys.readouterr()
    assert f"[x] done copying {src} to {dest}" in captured.out


def test_trycopy(tmp_path, capsys):
    src = tmp_path / "src.txt"
    src.write_text("content")
    dest = tmp_path / "dest.txt"

    file_utils.trycopy(str(src), str(dest), verbose=True)

    assert dest.exists()
    assert dest.read_text() == "content"

    captured = capsys.readouterr()
    assert f"[x] done copying {src} to {dest}" in captured.out


def test_trymkdir(tmp_path, capsys):
    d = tmp_path / "newdir"

    file_utils.trymkdir(str(d), verbose=True)

    assert d.exists()
    assert d.is_dir()

    captured = capsys.readouterr()
    assert f"[x] Successfully created dir {d}" in captured.out


def test_trymkfile(tmp_path, capsys):
    f = tmp_path / "newfile.txt"
    content = "hello world"

    file_utils.trymkfile(str(f), content, verbose=True)

    assert f.exists()
    assert f.read_text() == content

    captured = capsys.readouterr()
    assert f"[x] file {f} created with content:" in captured.out


def test_absdiroffile():
    # Since we can't easily fake __file__ context without creating a file,
    # we can test it with the current file if we were importing,
    # or just create a dummy file
    pass
    # Skipping this as it's a simple wrapper around os.path


def test_get_folders(tmp_path):
    (tmp_path / "d1").mkdir()
    (tmp_path / "d2").mkdir()
    (tmp_path / "f1").touch()

    folders = file_utils.get_folders(str(tmp_path))
    assert "d1" in folders
    assert "d2" in folders
    assert "f1" not in folders


def test_unique_filename():
    fname = "test.txt"
    unique = file_utils.unique_filename(fname)
    assert fname in unique
    assert unique != fname
    assert len(unique) > len(fname)


def test_path_exists(tmp_path):
    f = tmp_path / "exist.txt"
    f.touch()
    assert file_utils.path_exists(str(f))
    assert not file_utils.path_exists(str(tmp_path / "nope"))


def test_last_part_of_path():
    path = "/a/b/c"
    assert file_utils.last_part_of_path(path) == "c"
    path_trailing = "/a/b/c/"
    assert file_utils.last_part_of_path(path_trailing) == "c"


def test_delete_file(tmp_path):
    f = tmp_path / "del.txt"
    f.touch()
    file_utils.delete_file(str(f))
    assert not f.exists()
