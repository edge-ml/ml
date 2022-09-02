from app.codegen.inference.BasePlatform import BasePlatform
from app.codegen.inference.InferenceFormats import InferenceFormats
from app.internal.consts import SAMPLE_BASED_WINDOWING

class JavascriptPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Javascript"
    
    def supported_formats(self):
        return [InferenceFormats.JAVASCRIPT]

    def codegen(self, window_size, timeseries, labels, format, scaler, windowing_mode):
        tadd = ""
        for ts in timeseries:
            tadd = tadd + '\n    p.addDatapoint(\'{ts}\', get{ts}())'.format(ts = ts)

        return """const {{ Predictor }} = require('edge-ml')
const {{ score }} = require('./model_javascript')

const p = new Predictor(
    (input) => score(input),
    {timeseries_list}, // sensors
    {wsize}, // window size
    {labels}, // labels
    {scaler}, // scaler
    {{ // other options
        windowingMode: "{wmode}"
    }}
)

setInterval(() => {{{timeseries_add}

    p.predict()
        .then(x => x)
        .catch(e => console.log(e.message))
}}, 250)
""".format(
            wsize=window_size,
            timeseries_list=str(timeseries),
            labels=str(labels),
            timeseries_add=tadd,
            scaler=scaler,
            wmode="sample" if windowing_mode == SAMPLE_BASED_WINDOWING else "time"
        )