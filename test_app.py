import tempfile
import unittest
from pathlib import Path
from app import (
    Store, git, apply_edit, ToolEngine,
    create_checkpoint, restore_checkpoint,
    project_catalog, inspect_skills_compatibility
)


class SafetyAndFeaturesTest(unittest.TestCase):
    def test_agent_access_and_revocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = {'path': temporary}
            with self.assertRaises(PermissionError):
                apply_edit(project, 'test.txt', 'hello', None, lambda: True)
            project['access'] = 'Ask before edits'
            self.assertFalse(apply_edit(project, 'test.txt', 'hello', None, lambda: False))
            self.assertFalse((Path(temporary) / 'test.txt').exists())
            self.assertTrue(apply_edit(project, 'test.txt', 'hello', None, lambda: True))
            with self.assertRaises(ValueError):
                apply_edit(project, 'test.txt', 'replace', None, lambda: True)
            with self.assertRaises(ValueError):
                apply_edit(project, '../escape.txt', 'escape', None, lambda: True)

    def test_import_preserves_files_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / 'game'
            project.mkdir()
            asset = project / 'asset.txt'
            asset.write_text('original')
            store = Store(root / 'state')
            store.register(project)
            store.register(project)
            self.assertEqual(asset.read_text(), 'original')
            self.assertEqual(len(Store(root / 'state').data['projects']), 1)

    def test_git_error_is_visible(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(RuntimeError):
                git(temporary, 'status')

    def test_tool_sandbox_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            file_a = root / 'script.py'
            file_a.write_text('print("hello from sandbox")\nfor i in range(10): pass')

            # Test read_file
            content = ToolEngine.read_file(str(root), 'script.py')
            self.assertIn('hello from sandbox', content)

            # Test list_dir
            listing = ToolEngine.list_dir(str(root))
            self.assertIn('script.py', listing)

            # Test search_code
            matches = ToolEngine.search_code(str(root), 'range(10)')
            self.assertIn('script.py', matches)

            # Boundary violation
            with self.assertRaises(PermissionError):
                ToolEngine.read_file(str(root), '../forbidden.txt')

    def test_recovery_checkpoints(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            proj_dir = root / 'my_game'
            proj_dir.mkdir()
            (proj_dir / 'main.gd').write_text('extends Node\nfunc _ready(): pass')
            backup_dir = root / 'backups'
            project = {'path': str(proj_dir)}

            # Create checkpoint archive
            archive = create_checkpoint(project, str(backup_dir))
            self.assertTrue(Path(archive).is_file())

            # Restore into new folder
            restore_dest = root / 'restored_game'
            restore_checkpoint(archive, str(restore_dest))
            self.assertTrue((restore_dest / 'main.gd').is_file())
            self.assertEqual((restore_dest / 'main.gd').read_text(), 'extends Node\nfunc _ready(): pass')

            # Disallow restore to existing non-empty folder
            with self.assertRaises(ValueError):
                restore_checkpoint(archive, str(proj_dir))

    def test_team_connect_invariants(self):
        with tempfile.TemporaryDirectory() as temporary:
            store = Store(temporary)
            team_ai = store.data.get('team_ai', {})
            # Must be disabled by default
            self.assertFalse(team_ai.get('enabled'))
            # Must default to $0 cap
            self.assertEqual(team_ai.get('individual_cap_usd'), 0.0)
            # Must have immediate revocation enabled
            self.assertTrue(team_ai.get('immediate_revocation'))
            # Must prohibit automatic cost splitting
            self.assertFalse(team_ai.get('automatic_cost_splitting'))


if __name__ == '__main__':
    unittest.main()
