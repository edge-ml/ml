from app.utils.parameter_builder import ParameterBuilder
from app.ml.Pipelines.Categories.Classifier.utils import reshapeSklearn
from bson.objectid import ObjectId
import pickle
from app.Deploy.Sklearn.exportC_decisionTree import convert
from app.StorageProvider import StorageProvider

from app.ml.Pipelines.Abstract.AbstractPipelineOption import AbstractPipelineOption
from app.ml.Pipelines.AutoML.PytorchAdapter import get_dataloader
from tensorflow.keras import Model as KerasModel
from app.ml.Pipelines.PipelineContainer import PipelineContainer
from sklearn.model_selection import train_test_split as sklearn_train_test_split
from micronas import search, exec_tflm, PytorchKerasAdapter


class AutoMLClassifier(AbstractPipelineOption):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.data_id = None
        self.kerasModel : KerasModel = None
        self.tflmModel = None

    # static methods
    @staticmethod
    def get_parameters():
        pb = ParameterBuilder()
        pb.parameters = []

        pb.add_number(
            "peak_mem_limit",
            "Peak Memory Limit",
            "The maximum allowed peak memory size.",
            3000,
            50000,
            None,
            1,
            False,
            False,
        )
        return pb.parameters


    @staticmethod
    def get_name():
        return "AutoML Classifier"

    @staticmethod
    def get_description():
        return "Uses neural architecture search to find a suitable classifier"

    @staticmethod
    def get_platforms():
        return []

    def exportC(self):
        return convert(self.clf)

    # class methods
    def __init__(self, parameters=[]):
        super().__init__(parameters)

    def fit_exec(self, data):
        print("*"*20)
        print("DATASHAPE: ", data.data.shape)
        train_data = data.data[:,:,1:]
        train_labels = data.labels
        print(train_data.shape)

        train_split, vali_split, train_label_split, vali_label_split = sklearn_train_test_split(train_data, train_labels)

        dataset_train = get_dataloader(train_split, train_label_split)
        dataset_vali = get_dataloader(vali_split, vali_label_split)
        
        kerasModel, tflmModel = search(dataset_train, dataset_vali, 2, config={"train_epochs": 200})
        self.kerasModel = kerasModel
        self.tflmModel = tflmModel

    def exec(self, data):
        exec_data = data.data[:,:,1:]
        dataloaderKeras = PytorchKerasAdapter(get_dataloader(exec_data, data.labels), 2)
        pred = exec_tflm(dataloaderKeras, self.tflmModel)
        return PipelineContainer(pred, data.labels, data.meta)


    def fit(self, X_train, y_train):
        pass
        # X_train_reshaped = reshapeSklearn(X_train)
        # self.clf.fit(X_train_reshaped, y_train)

    def predict(self, X_test):
        pass

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error
    
    def get_state(self):
        return {"data_id": self.data_id}

    def restore(self, dict):
        self.data_id = dict.state["data_id"]
        byte_clf = StorageProvider.load(self.data_id)
        self.clf = pickle.loads(byte_clf)

    def persist(self):
        self.data_id = ObjectId()
        byte_clf = pickle.dumps(self.tflmModel)
        StorageProvider.save(self.data_id, byte_clf)
        return super().persist()