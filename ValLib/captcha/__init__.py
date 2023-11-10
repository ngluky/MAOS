from .alternative import set_solver, solver
from .struct import CaptchaSolver
from .web import WebServerSolver
from .exceptions import HCaptchaTimeoutException

__all__ = [
    "CaptchaSolver", "WebServerSolver",
    "set_solver", "solver",
    "HCaptchaTimeoutException"
]
