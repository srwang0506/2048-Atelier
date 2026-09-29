import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from engine import Game,Storage
import platform_paths

class PortableRegressionTests(unittest.TestCase):
    def test_missing_main_save_recovers_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'save.json';store=Storage(path);game=Game(19)
            self.assertTrue(store.save(game,{}));expected=game.snapshot()
            game.move('left');self.assertTrue(store.save(game,{}));path.unlink()
            restored=Storage(path)
            self.assertIsNone(restored.error);self.assertTrue(restored.notice)
            self.assertEqual(Game.restore(restored.data['game']).snapshot(),expected)
            self.assertTrue(restored.save(Game.restore(restored.data['game']),{}))
            self.assertIsNone(Storage(path).error)

    def test_chinese_assets_do_not_use_system_ansi_encoding(self):
        import puzzles,rescue
        real=Path.read_text
        def windows_read(path,*args,**kwargs):
            if path.name in ('puzzle_levels.json','rescue_practice.json'):
                if not args and 'encoding' not in kwargs:kwargs['encoding']='cp1252'
            return real(path,*args,**kwargs)
        with patch.object(Path,'read_text',windows_read):
            importlib.reload(puzzles)
            self.assertEqual(puzzles.LEVELS[0]['title'],'借一步')
            self.assertEqual(len(rescue.practice_challenges()),3)
            self.assertEqual(rescue.practice_challenges()[0]['title'],'一线生机')

    def test_windows_paths_and_non_destructive_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'Game 2048 中文';(root/'data').mkdir(parents=True)
            user=Path(folder)/'User 中文'
            game=Game(11);self.assertTrue(Storage(root/'data/save.json').save(game,{}))
            with patch.object(platform_paths,'ROOT',root),patch.object(sys,'platform','win32'),patch.dict(os.environ,{'LOCALAPPDATA':str(user)}):
                self.assertEqual(platform_paths.save_path(),user/'2048-Atelier/data/save.json')
                self.assertEqual(platform_paths.save_path(True),root/'data/demo.json')
                platform_paths.prepare_data()
                target=platform_paths.save_path();self.assertEqual(Game.restore(Storage(target).data['game']).snapshot(),game.snapshot())
                other=Game(33);Storage(target).save(other,{})
                platform_paths.prepare_data()
                self.assertEqual(Game.restore(Storage(target).data['game']).snapshot(),other.snapshot())

    def test_instance_lock_blocks_second_process_and_releases(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'game.lock'
            code="from platform_paths import InstanceLock,AlreadyRunning\nimport sys\ntry:\n with InstanceLock(sys.argv[1]): pass\nexcept AlreadyRunning: sys.exit(4)"
            command=[sys.executable,'-c',code,str(path)]
            with platform_paths.InstanceLock(path):
                self.assertEqual(subprocess.run(command,cwd=platform_paths.ROOT,timeout=10).returncode,4)
            self.assertEqual(subprocess.run(command,cwd=platform_paths.ROOT,timeout=10).returncode,0)

    def test_screenshot_write_failure_is_not_a_crash(self):
        import interface_base as controller
        import pygame as pg
        a=object.__new__(controller.Atelier);a.toasts=[];a.canvas=None
        with tempfile.TemporaryDirectory() as folder,patch.object(controller,'export_dir',return_value=Path(folder)),patch.object(pg.image,'save',side_effect=pg.error('disk full')):
            a.act('export')
        self.assertIn('截图保存失败',a.toasts[-1][0])

    def test_windows_has_bundled_real_weights_without_system_cjk(self):
        import typography
        typography.families.cache_clear()
        try:
            with patch.object(sys,'platform','win32'):
                faces=typography.families()
                self.assertEqual(len({path for path,index in faces.values()}),3)
                self.assertTrue(all(Path(path).is_file() for path,index in faces.values()))
                self.assertTrue(all('NotoSansSC-' in path for path,index in faces.values()))
        finally:typography.families.cache_clear()

if __name__=='__main__':unittest.main()
