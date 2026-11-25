class PipelineContainer():
    def __init__(self, data, labels, meta, layout=None) -> None:
        self.data = data
        self.labels = labels
        self.meta = meta
        # How the columns of a packed feature array split into the inputs of a
        # multi-input model (audio pipeline); None for every other pipeline.
        self.layout = layout
