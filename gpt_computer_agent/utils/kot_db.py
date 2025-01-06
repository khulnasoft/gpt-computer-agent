try:
    from .folder import artifacts_dir  # import only what's needed
except ImportError:
    from folder import artifacts_dir
from kot import KOT
kot_db_ = KOT("gca", folder=artifacts_dir, enable_hashing=True)