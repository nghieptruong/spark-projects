from pyspark import SparkContext, SparkConf, StorageLevel
from pyspark.streaming import StreamingContext


checkpoint_dir = "checkpoint-online-wordcount"

def startSSC():
        conf = SparkConf().set("spark.streaming.receiver.writeAheadLog.enable" , "true")
        sc = SparkContext("local[*]", "NetworkWordCount")
        ssc = StreamingContext(sc, 1)
        ssc.checkpoint(checkpoint_dir)

        lines = ssc.socketTextStream("localhost", 9999, StorageLevel.MEMORY_ONLY)
        words = lines.flatMap(lambda line: line.split())
        pairs = words.map(lambda word: (word, 1))
        wordCounts = pairs.reduceByKey(lambda x, y: x + y)

        #Window Operation
        windowedWordCounts = pairs.\
                filter(lambda pair: pair[0].\
                startswith("#")).\
                reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, 30, 10)

        # Save the raw data in HDFS
        lines.saveAsTextFiles("data/raw","text")

        # Print the values of the word counts in window
        windowedWordCounts.pprint(25)

        return ssc


ssc = StreamingContext.getOrCreate(checkpoint_dir, startSSC)

ssc.start()             # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate
