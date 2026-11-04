"""脚本公用：按项目目录加载它的 mv.py（frame、DUR）。"""
import importlib.util, os, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(project):
    project = os.path.abspath(project)
    os.environ['PIXMV_PROJECT'] = project
    os.environ.setdefault('PIXMV_SKILL', SKILL)
    sys.path.insert(0, os.path.join(SKILL, 'lib'))
    sys.path.insert(0, project)
    spec = importlib.util.spec_from_file_location('mv', os.path.join(project, 'mv.py'))
    m = importlib.util.module_from_spec(spec)
    sys.modules['mv'] = m
    spec.loader.exec_module(m)
    return m
