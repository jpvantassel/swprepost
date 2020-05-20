class_names = ["Curve",
               "CurveUncertain",
               "DispersionCurve",
               "DispersionSet",
               "DispersionSuite",
               "GroundModel",
               "GroundModelSuite",
               "Parameter",
               "Parameterization",
               "Suite",
               "Target"]

for class_name in class_names:

    contents = f""".. _{class_name.lower()}:

{class_name}
{"="*len(class_name)}

.. automodule:: swprepost.{class_name.lower()}
    :members:
    :undoc-members:
    :show-inheritance:
"""

    with open("docs/"+class_name.lower()+".rst", "w", encoding="utf8") as f:
        f.write(contents)

