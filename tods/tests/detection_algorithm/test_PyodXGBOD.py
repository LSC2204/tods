import unittest

from d3m import container, utils
from d3m.metadata import base as metadata_base
from d3m.container import DataFrame as d3m_dataframe

from tods.detection_algorithm.PyodXGBOD import XGBODPrimitive
from pyod.utils.data import generate_data

from tods.detection_algorithm.core.SODCommonTest import SODCommonTest

import numpy as np

class PyodXGBODTestCase(unittest.TestCase):
    def setUp(self):

        self.maxDiff = None
        self.n_train = 200
        self.n_test = 100
        self.contamination = 0.1
        self.roc_floor = 0.8 
        self.X_train, self.y_train, self.X_test, self.y_test = generate_data(
            n_train=self.n_train, n_test=self.n_test,
            contamination=self.contamination, random_state=42)

        self.X_train = d3m_dataframe(self.X_train, generate_metadata=True)
        self.y_train = d3m_dataframe(self.y_train, generate_metadata=True)
        self.X_test = d3m_dataframe(self.X_test, generate_metadata=True)

        hyperparams_default = XGBODPrimitive.metadata.get_hyperparams().defaults()
        hyperparams = hyperparams_default.replace({'contamination': self.contamination, })

        self.primitive = XGBODPrimitive(hyperparams=hyperparams)

        self.primitive.set_training_data(inputs=self.X_train, outputs=self.y_train)
        self.primitive.fit()
        self.prediction_labels = self.primitive.produce(inputs=self.X_test).value
        self.prediction_score = self.primitive.produce_score(inputs=self.X_test).value

        self.sodbase_test = SODCommonTest(model=self.primitive._clf,
                                          X_train=self.X_train.values, # added .values
                                          y_train=self.y_train.values, # added .values
                                          X_test=self.X_test.values, # added .values
                                          y_test=self.y_test,
                                          roc_floor=self.roc_floor,
                                          )

    def test_detector(self):
        self.sodbase_test.test_detector()


    def test_metadata(self):
        # print(utils.to_json_structure(self.prediction_labels.metadata.to_internal_simple_structure()))

        metadata_one = [{
            'selector': [],
            'metadata': {
                'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
                'structural_type': 'd3m.container.pandas.DataFrame',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/Table'],
                'dimension': {
                    'name': 'rows',
                    'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                    'length': 100,
                },
            },
        }, {
            'selector': ['__ALL_ELEMENTS__'],
            'metadata': {
                'dimension': {
                    'name': 'columns',
                    'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                    'length': 1,
                },
            },
        }, {
            'selector': ['__ALL_ELEMENTS__', 0],
            'metadata': {
                'structural_type': 'numpy.float64',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/Attribute', 'https://metadata.datadrivendiscovery.org/types/PredictedTarget'],
            },
        }]

        metadata_two = [{
            'selector': [],
            'metadata': {
                'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
                'structural_type': 'd3m.container.pandas.DataFrame',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/Table'],
                'dimension': {
                    'name': 'rows',
                    'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                    'length': 100,
                },
            },
        }, {
            'selector': ['__ALL_ELEMENTS__'],
            'metadata': {
                'dimension': {
                    'name': 'columns',
                    'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                    'length': 1,
                },
            },
        }, {
            'selector': ['__ALL_ELEMENTS__', 0],
            'metadata': {
                'structural_type': 'numpy.float64',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/PredictedTarget', 'https://metadata.datadrivendiscovery.org/types/Attribute'],
            },
        }]

        self.assertTrue(utils.to_json_structure(self.prediction_labels.metadata.to_internal_simple_structure()) in [metadata_one, metadata_two])

    def test_params(self):
        params = self.primitive.get_params()
        self.primitive.set_params(params=params)

if __name__ == '__main__':
    unittest.main()
