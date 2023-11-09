from app.ml.PipelineExport.C.Common.CPart import CStep, ExtraFile
from app.ml.PipelineExport.C.Common.utils import getCode
from jinja2 import Template
import math

from typing import List

def buildCCode(steps: List[CStep], model):

    # for (lastStep, step) in zip(steps[:-1], steps[1:]):
    #     mem = lastStep.output_mem.bytes + step.input_mem.bytes
    #     print(mem)

    for i, step in enumerate(steps):
        print("step: ", step)
        print(step.compile(name=f"step_{i}"))

    compiled_steps = [step.compile(name=f"step_{i}") for i, step in enumerate(steps)]
    globals = []
    for step in steps:
        globals.extend(step.globals)
    base_code = getCode("./app/ml/PipelineExport/C/Base.cpp")

    includes = []
    for step in steps:
        includes.extend(step.includes)

    for step in steps:
        print("CCOMPILE: ", step.input_shape, step.output_shape)

    output_matrices = []
    for i, step in enumerate(steps):
        if len(step.output_shape) == 2:
            output_matrices.append({"name": f"step_{i}_output", "init": f"Matrix step_{i}_output({step.output_shape[0]}, vector<float>({step.output_shape[1]}));"})
    globals.extend([x["init"] for x in output_matrices])

    predictSteps = []
    for i, step in enumerate(steps):
        if i == 0:
            continue
        if i == len(steps)-1:
            predictSteps.append(f"return step_{i}(step_{i-1}_output);")
            continue
        predictSteps.append(f"step_{i}(step_{i-1}_output, step_{i}_output);")


    template = Template(base_code)
    rendered_code = template.render({
        "steps": compiled_steps,
        "globals": globals,
        "includes": includes,
        "predictSteps": predictSteps,
        "labels": [x.name for x in model.labels],
        "samplingRate": math.floor(model.samplingRate * 100) / 100,
        "enumerate": enumerate,})

    print("*" * 40, "RENDERED_CODE", "*" * 40)

    print(rendered_code)

    files = []
    for step in steps:
        files.extend(step.extra_files)
    files.append(ExtraFile("model.cpp", rendered_code))

    return files

    # with open("/Users/king/Desktop/testCpp/test.cpp", "w") as f:
    #     f.write(rendered_code)

        