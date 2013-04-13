import sqlite3
import recsys.algorithm
recsys.algorithm.VERBOSE = True

from recsys.algorithm.factorize import SVD
from recsys.evaluation.prediction import RMSE, MAE

from recsys.datamodel.data import Data
from recsys.datamodel.item import Item
from recsys.datamodel.user import User

data = Data()
data.load("../data/ratings.tsv", sep='|', format={'col':0, 'row':1, 'value':2, 'ids':float})

K=100
svd = SVD()
svd.set_data(data)
svd.compute(k=K, min_values=0.1, pre_normalize=None, mean_center=True, post_normalize=True)

[(beers[b].get_data()['name'], b, val) for b, val in  svd.similar(1502, 50)\
 if beers[b].get_data()['brewery']!=232 and beers[b].get_data()['style_id']==17] #Bell's two hearted