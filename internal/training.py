import pandas as pd
import tsfresh
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train(df_sliding_window, data_y):
    settings = tsfresh.feature_extraction.settings.MinimalFCParameters()
    data_x = tsfresh.extract_features(df_sliding_window, column_id="id", default_fc_parameters=settings) 
    x_train, x_test, y_train, y_test = train_test_split(data_x, data_y, random_state = 5, test_size=0.33) # TODO fix hardcoded
    scaler = RobustScaler()
    scaler.fit(x_train)
    trans_x_train = scaler.transform(x_train)
    trans_x_test = scaler.transform(x_test)
    trans_x_train = pd.DataFrame(trans_x_train,columns=x_train.columns)
    trans_x_test = pd.DataFrame(trans_x_test,columns=x_test.columns)
    trans_x_train.describe()
    clf = RandomForestClassifier()
    clf.fit(trans_x_train,y_train)
    y_pred = clf.predict(trans_x_test)
    print("accuracy_score train :", accuracy_score(y_test, y_pred))
    return clf