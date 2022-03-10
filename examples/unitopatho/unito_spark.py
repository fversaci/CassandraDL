# Copyright 2021-2 CRS4
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

# Run with, e.g.,
# /spark/bin/spark-submit --master spark://$HOSTNAME:7077 --conf spark.default.parallelism=20 --py-files unito_common.py unito_spark.py --src-dir /data/unitopath-public/

import os
import argparse
from getpass import getpass
import unito_common
from pyspark import StorageLevel
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession


def run(args):
    # Read Cassandra parameters
    try:
        from private_data import cassandra_ip, cass_user, cass_pass
    except ImportError:
        cassandra_ip = getpass("Insert Cassandra's IP address: ")
        cass_user = getpass("Insert Cassandra user: ")
        cass_pass = getpass("Insert Cassandra password: ")

    # run spark
    conf = SparkConf().setAppName("UNITOPatho")
    # .setMaster("spark://spark-master:7077")
    sc = SparkContext(conf=conf)
    spark = SparkSession(sc)
    src_dir = args.src_dir
    for suffix in ["7000_224", "800"]:
        cur_dir = os.path.join(src_dir, suffix)
        jobs = unito_common.get_jobs(cur_dir)
        par_jobs = sc.parallelize(jobs)
        par_jobs.foreachPartition(
            unito_common.save_images(cassandra_ip, cass_user, cass_pass, suffix)
        )


# parse arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--src-dir",
        metavar="DIR",
        required=True,
        help="Specifies the input directory for UNITOPatho",
    )
    run(parser.parse_args())
