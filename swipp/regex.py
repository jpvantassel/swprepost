import re

number = r"\d+.?\d*[eE]?[+-]?\d*"

# DC
pair = f"{number} {number}\n"
model_txt = r"# Layered model (\d+): value=(\d+.?\d*)"
wave_txt = r"# \d+ (Rayleigh|Love) dispersion mode\(s\)"
mode_txt = r"# Mode \d+\n"
dcset_txt = f"{model_txt}\n{wave_txt}\n.*\n((?:{mode_txt}(?:{pair})+)+)"

model = re.compile(model_txt)
mode = re.compile(mode_txt)
dcset = re.compile(dcset_txt)
dc_data = re.compile(f"({number}) ({number})")

# GM
quad = f"{number} {number} {number} {number}\n"
gm_txt = f"{model_txt}\n\d+\n((?:{quad})+)"

gm = re.compile(gm_txt)
gm_data = re.compile(f"({number}) ({number}) ({number}) ({number})")
