from io import BytesIO

class BaseDataLoader():

    def load_series(self, id, path):
        raise NotImplementedError()

    def save_series(self, id, time_arr, data_arr):
        raise NotImplementedError()
    
    def saveObj(self, id, obj: BytesIO):
        raise NotImplementedError()

    def loadObj(self, id) -> BytesIO:
        raise NotImplementedError()
    
    def delete(self, id):
        raise NotImplementedError()

    def load_media_to_file(self, media_id, path):
        """Copy the original file of a recording (stored by the dataset-store
        under media/{id}) to a local path."""
        raise NotImplementedError()