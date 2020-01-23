import re

data = re.compile(r"^(\d+.?\d*[eE]?[+-]?\d*) (\d+.?\d*[eE]?[+-]?\d*)$")
model = re.compile(r"^# Layered model (\d+): value=(\d+.?\d*)$")
wave = re.compile(r"^# \d+ (Rayleigh|Love) dispersion mode\(s\)$")
mode = re.compile(r"^# Mode (\d+)")
