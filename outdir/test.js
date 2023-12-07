const fs = require('fs');
const { promisify } = require('util');
const sleep = promisify(setTimeout);
const model = require('./model.js')

// const CSV_FILE_PATH = '{{ csv_file_path }}';
// const DATAPOINTS_TO_READ = {{ datapoints_to_read }};
// const WINDOW_SIZE = {{ window_size }};
const CSV_FILE_PATH = '/home/omer/WorkRepos/ml/tests/fixtures/test_divergence/test_data.csv';
const DATAPOINTS_TO_READ = 375;
const WINDOW_SIZE = 20;

const node_json = { windowed: [], features: [], normalized: [], predictions: [] };

async function main() {
    try {
        const instance = await model()
        const file = fs.createReadStream(CSV_FILE_PATH);
        const readline = require('readline');
        const rl = readline.createInterface({ input: file, crlfDelay: Infinity });

        let data_count = 0;
        let raw_data = [];
        let features = [];

        for await (const line of rl) {
            if (data_count >= DATAPOINTS_TO_READ) break;

            const [x_str, y_str, z_str] = line.split(',');

            const x = parseFloat(x_str);
            const y = parseFloat(y_str);
            const z = parseFloat(z_str);

            instance.add_datapoint(x, y, z);
            data_count++;

            if (false) {
            // if ({{ time_windowing }}) {
                // node_json.windowed.push(raw_data);
                // extract_features(raw_data, features);
                // node_json.features.push(features);
                // normalize(features);
                // node_json.normalized.push(features);
                const prediction = instance.predict();

                node_json.predictions.push(prediction);

                // await sleep({{ time_window_sep_interval }});
            } else if (data_count >= WINDOW_SIZE) {
                // node_json.windowed.push(raw_data);
                // extract_features(raw_data, features);
                // node_json.features.push(features);
                // normalize(features);
                // node_json.normalized.push(features);
                const prediction = instance.predict();

                console.log(`${data_count}: ${prediction} ${instance.class_to_label(prediction)}`)

                node_json.predictions.push(prediction);
            }
        }

        // console.log(JSON.stringify(node_json, null, 4));
    } catch (err) {
        console.error('Error:', err);
    }
    
    console.log('%j', node_json.predictions)
}

main();