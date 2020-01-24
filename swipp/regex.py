import re

number = r"\d+.?\d*[eE]?[+-]?\d*"
pair = f"{number} {number}\n"
model_txt = r"# Layered model (\d+): value=(\d+.?\d*)"
wave_txt = r"# \d+ (Rayleigh|Love) dispersion mode\(s\)"
mode_txt = r"# Mode \d+\n"
dcset_txt = f"{model_txt}\n{wave_txt}\n.*\n((?:{mode_txt}(?:{pair})+)+)"

data = re.compile(f"({number}) ({number})")
model = re.compile(model_txt)
dcset = re.compile(dcset_txt)
mode = re.compile(mode_txt)
gm = re.compile(f"^({number}) ({number}) ({number}) ({number})$")
