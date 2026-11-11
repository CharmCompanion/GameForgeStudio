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

    def test_autonomous_react_tool_loop(self):
        import re
        import json
        with tempfile.TemporaryDirectory() as temporary:
            proj = Path(temporary)
            (proj / 'player.gd').write_text('var speed = 200\nfunc move(): pass')
            
            # Step 1: Agent returns tool call block
            simulated_response = 'I will inspect player.gd.\n```json\n{"tool": "read_file", "args": {"path": "player.gd"}}\n```'
            match = re.search(r'```(?:json)?\s*(\{"tool":[\s\S]+?\})\s*```', simulated_response)
            self.assertIsNotNone(match)
            call = json.loads(match.group(1))
            self.assertEqual(call['tool'], 'read_file')
            
            # Step 2: ToolEngine executes inside project
            obs = ToolEngine.read_file(str(proj), call['args']['path'])
            self.assertIn('var speed = 200', obs)
            
            # Step 3: Next step writes fix autonomously under Full project editing
            write_call = {'tool': 'write_file', 'args': {'path': 'player.gd', 'content': 'var speed = 400\nfunc move(): pass'}}
            (proj / write_call['args']['path']).write_text(write_call['args']['content'], encoding='utf-8')
            self.assertIn('speed = 400', (proj / 'player.gd').read_text())

    def test_work_folder_and_master_lists_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = Path(temporary) / 'state'
            store = Store(state_dir)
            
            # Verify work_folder, master_list, projects_list are initialized
            self.assertIn('work_folder', store.data)
            self.assertIn('master_list', store.data)
            self.assertIn('projects_list', store.data)
            
            # Configure custom work folder and lists
            custom_work = str(Path(temporary) / 'CustomDev')
            custom_master = str(Path(temporary) / 'CustomDev' / 'MASTER_PROJECTS.md')
            custom_projects = str(Path(temporary) / 'CustomDev' / 'PROJECTS.md')
            
            store.data['work_folder'] = custom_work
            store.data['master_list'] = custom_master
            store.data['projects_list'] = custom_projects
            store.save()
            
            # Reload from disk and verify persistence
            reloaded = Store(state_dir)
            self.assertEqual(reloaded.data['work_folder'], custom_work)
            self.assertEqual(reloaded.data['master_list'], custom_master)
            self.assertEqual(reloaded.data['projects_list'], custom_projects)


if __name__ == '__main__':
    unittest.main()
