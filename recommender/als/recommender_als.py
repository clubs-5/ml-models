from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler,VectorIndexer,OneHotEncoder,StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
import time
from pyspark.sql.types import StructType,StructField, StringType, IntegerType

if __name__ == "__main__":

    spark = SparkSession \
        .builder \
        .getOrCreate()

    # Prepare data
    final_data = spark.read.csv("hdfs://master.tibame/user/clubs/ml-25m/ratings.csv",
                                inferSchema=True,
                                header=True)

    # Split data into train and test sets
    train_data, test_data = final_data.randomSplit([0.8,0.2])
    
    # Model training
    als = ALS(maxIter=10,userCol="userId",itemCol="movieId",ratingCol="rating" , coldStartStrategy="drop")
    start=time.time()
    model = als.fit(train_data)
    
    # Transform the test data using the model to get predictions
    predicted_test_data = model.transform(test_data)
    model.write().overwrite().save("hdfs://master.tibame/user/clubs/spark_mllib_101/movies/movies_recommender/")

    # Evalute model performance with test set
    evaluator = RegressionEvaluator(predictionCol="prediction", labelCol="rating", metricName="rmse")
    #print("rmse: {}".format(evaluator.evaluate(predicted_test_data)))
    stop=time.time()
    print(stop-start)

    # Specify the number of movies you would like to recommand for each user
    user_movies = model.recommendForAllUsers(5)
    user_movies.show(100, truncate=False)
    user_movies.printSchema()

    print(type(user_movies))

    # return specific user result
    #result = user_movies.filter(user_movies.userId == 544).collect()
    #print(result)

    # Generate top 10 movie recommendations for a specified set of users
    #users = final_data.select(als.getUserCol()).distinct().limit(3)
    #userSubsetRecs = model.recommendForUserSubset(users, 10)
    # The users who are most likely to like a particular movie
    #movie_uers = model.recommendForAllItems(3)
    #movie_uers.show(100, truncate=False)
    
