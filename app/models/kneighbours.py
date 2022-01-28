from app.utils.parameter_builder import ParameterBuilder
from app.models.edge_model import EdgeModel
from sklearn.neighbors import KNeighborsClassifier
import copy


class KNeighbours(EdgeModel):
    # static methods
    @staticmethod
    def get_hyperparameters():
        pb = copy.deepcopy(
            ParameterBuilder(EdgeModel.get_hyperparameters())
        )  # get base parameter

        pb.add_number(
            "n_neighbors",
            "N Neighbours",
            "Number of neighbors to use by default for kneighbors queries. Needs to be less than the number of samples in the fitted data",
            1,
            100,
            1,
            1,
            True,
        )

        pb.add_selection(
            "weights",
            "Weights",
            "Weight function used in prediction. Possible values: ‘uniform’ : All points in each neighborhood are weighted equally. ‘distance’ : weight points by the inverse of their distance. in this case, closer neighbors of a query point will have a greater influence than neighbors which are further away.",
            ["uniform", "distance"],
            "uniform",
            False,
            True,
        )

        pb.add_selection(
            "algorithm",
            "Algorithm",
            "Algorithm used to compute the nearest neighbors. Note: fitting on sparse input will override the setting of this parameter, using brute force.",
            ["auto", "ball_tree", "kd_tree", "brute"],
            "auto",
            False,
            True,
        )

        pb.add_number(
            "leaf_size",
            "Leaf Size",
            "Leaf size passed to BallTree or KDTree. This can affect the speed of the construction and query, as well as the memory required to store the tree. The optimal value depends on the nature of the problem.",
            1,
            100000,
            30,
            1,
            True,
            False,
        )

        pb.add_number(
            "p",
            "Power Parameter",
            "Power parameter for the Minkowski metric. When p = 1, this is equivalent to using manhattan_distance (l1), and euclidean_distance (l2) for p = 2. For arbitrary p, minkowski_distance (l_p) is used.",
            1,
            1000,
            1,
            1,
            True,
            False,
        )

        pb.add_selection(
            "metric",
            "Metric",
            "The distance metric to use for the tree. The default metric is minkowski, and with p=2 is equivalent to the standard Euclidean metric. For a list of available metrics, see the documentation of DistanceMetric. If metric is “precomputed”, X is assumed to be a distance matrix and must be square during fit. X may be a sparse graph, in which case only “nonzero” elements may be considered neighbors.",
            [
                "euclidean",
                "manhattan",
                "chebyshev",
                "minkowski",
                "wminkowski",
                "seuclidean",
                "mahalanobis",
                "haversine",
                "hamming",
                "canberra",
                "braycurtis",
                "jaccard",
                "matching",
                "dice",
                "kulsinski",
                "rogerstanimoto",
                "russellrao",
                "sokalmichener",
                "sokalsneath",
            ],
            "minkowski",
            False,
            True,
        )

        # metric params takes dict
        # pb.add_selection('metric_params')

        # user should not be able to set this
        # pb.add_number(
        #     "n_jobs",
        #     "N Jobs",
        #     "The number of jobs to run in parallel. fit, predict, decision_path and apply are all parallelized over the trees. None means 1 unless in a joblib.parallel_backend context. -1 means using all processors.",
        #     -1,
        #     10000,
        #     None,
        #     1,
        #     True,
        #     False,
        # )

        return pb.parameters

    @staticmethod
    def get_name():
        return "K-Nearest Neighbours Classifier"

    @staticmethod
    def get_description():
        return "A simple K-Nearest Neighbours classifier."

    # class methods
    def __init__(self):
        super()
        self.clf = KNeighborsClassifier()

    def compile(self):
        if not self.is_fit:
            return
            # TODO: throw error
