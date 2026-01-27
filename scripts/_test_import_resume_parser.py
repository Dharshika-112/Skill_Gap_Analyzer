import importlib.util

p = 'backend/app/services/resume_parser.py'
spec = importlib.util.spec_from_file_location('resume_parser', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('loaded parse_resume:', hasattr(mod, 'parse_resume'))
print('loaded extract_skills_from_text:', hasattr(mod, 'extract_skills_from_text'))
