def prompts(name, description):
    def decorator(func):
        func.name = name
        func.description = description
        return func

    return decorator


class ToolName:
    def __init__(self):
        # write the initialization code here
        # according to your design
        pass

    @prompts(name="THE TOOLS MEANINGFUL NAME",
             description="THE TOOLS MEANINGFUL DESCRIPTION")
    def forward(self, inputs):
        pass